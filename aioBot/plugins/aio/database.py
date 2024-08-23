# Copyright (C) 2024 originalFactor
#
# This file is part of QwenBotQ.
#
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

'The database module of QwenBotQ'

# standard import
from typing import Union, List
from datetime import datetime, timedelta
from os.path import isdir, split
from os import mkdir, listdir, remove
# third-party import
from pydantic import BaseModel, field_validator
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, HTTPError
from nonebot import logger
# local import
from . import config
from .utils import still_valid

http_client = AsyncClient()


class User(BaseModel):
    'The user model of QwenBotQ'

    id: str
    permission: int = 0
    system_prompt: str = config.system_prompt
    coins: int = 0
    last_signed_date: datetime = datetime(1970, 1, 1)

    async def get_avatar_path(self) -> Union[str, None]:
        'Get the avatar path of the user'
        if not isdir('cache'):
            mkdir('cache')
        base_dir = f'cache/{self.id}'
        if not isdir(base_dir):
            mkdir(base_dir)
        files = listdir(base_dir)
        return base_dir+'/'+files[0] if files else None

    @property
    async def avatar(self) -> bytes:
        'Get the avatar of the user'
        file = await self.get_avatar_path()
        if not file or not await still_valid(
                datetime.fromtimestamp(float(split(file)[1].split('.')[0]))):
            try:
                resp = await http_client.get(f"http://q1.qlogo.cn/g?b=qq&nk={self.id}&s=640")
                resp.raise_for_status()
                content = resp.content
                if file:
                    remove(file)
                with open(f'cache/{self.id}/{int(datetime.now().timestamp())}.png', 'wb') as f:
                    f.write(content)
                return content
            except HTTPError as e:
                logger.warning(
                    'Avartar download failed, using the old one.'
                    f' Exception: {e}'
                )
        if file:
            with open(file, 'rb') as f:
                return f.read()
        return b''

    @property
    async def couple(self) -> Union["Couple", None]:
        'Get the couple of the user'
        return await find_couple(self.id)

    @property
    async def sign_expire(self) -> datetime:
        'Get the daily sign expire time of the user'
        return self.last_signed_date+timedelta(1)

    @field_validator('permission')
    @classmethod
    def validate_permission(cls, v: int) -> int:
        'Validate the permission field of the user'
        if v > 999:
            return 999
        if v < 0:
            return 0
        return v


class Couple(BaseModel):
    'The couple model of QwenBotQ'
    A: str
    B: str
    date: datetime

    async def opposite(self, me: str) -> str:
        'Get the opposite of the couple'
        return self.A if self.B == me else self.B

    @property
    async def expire(self) -> datetime:
        'Get the expire time of the couple'
        return self.date+timedelta(1)


database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]

users = database['users']

couples = database['couples']

nicks = database['nicks']


async def initialize_database():
    'Initialize the database.'
    await users.delete_many({})
    await users.drop_indexes()
    await users.insert_many([User(id=_, permission=999).model_dump() for _ in config.supermgr_ids])
    await users.create_index('id', unique=True)
    await couples.delete_many({})
    await couples.drop_indexes()
    await couples.insert_one(Couple(A='0', B='0', date=datetime.fromtimestamp(0)).model_dump())
    await couples.create_index(['A'], unique=True)
    await couples.create_index(['B'], unique=True)
    await nicks.delete_many({})
    await nicks.create_index('id', unique=True)


async def get_user(identity: Union[str, int]) -> User:
    'Get the user from the database if it exists, otherwise create a new one'
    if _ := await users.find_one({'id': str(identity)}):
        return User(**_)
    user = User(id=str(identity))
    await create_user(user)
    return user


async def create_user(user: Union[User, "UserWithNick"]):
    'Create a new user in the database'
    await users.insert_one((await uwn2u(user)).model_dump())


async def update_user(user: Union[User, "UserWithNick"]):
    'Update the user in the database'
    await users.update_one({'id': user.id}, {'$set': (await uwn2u(user)).model_dump()})


async def find_couple(x: Union[str, None], invaild: bool = False) -> Union[Couple, None]:
    'Find the couple of the user'
    tmp = await couples.find_one({'$or': [{'A': x}, {'B': x}]})
    return Couple(**tmp) if tmp and (invaild or await still_valid(tmp['date'])) else None


async def remove_couple(cp: Couple):
    'Remove the couple from the database'
    await couples.delete_many({
        "$or": [
            {'A': cp.A},
            {'A': cp.B},
            {'B': cp.A},
            {'B': cp.B}
        ]
    })


async def use_couple(cp: Couple):
    'Change the database to match the given couple.'
    await remove_couple(cp)
    await couples.insert_one(cp.model_dump())


async def get_top10_users() -> List[User]:
    'Get the top 10 users sorted by coins'
    result = []
    async for document in users.find({}).sort('coins', -1).limit(10):
        result.append(User(**document))
    return result


class NickCache(BaseModel):
    'The nick cache model of QwenBotQ'
    id: str
    nick: str
    created: datetime


async def find_nick(identity: str, invaild: bool = False) -> Union[NickCache, None]:
    'find the nick of the user from the cache database if it exists, otherwise return None'
    return (
        NickCache(**_)
        if (
            (_ := await nicks.find_one({'id': identity}))
            and
            (invaild or await still_valid(_['created']))
        )
        else None
    )


async def remove_nick(identity: str):
    'Remove the nick of the user from the caching database'
    await nicks.delete_many({'id': identity})


async def use_nick(nick: NickCache):
    'Set the nick of the user in the caching database'
    await remove_nick(nick.id)
    await nicks.insert_one(nick.model_dump())


class UserWithNick(User):
    'The user model with nick'
    nick: str


async def uwn2u(user: Union[User, UserWithNick]) -> User:
    'Convert the user model with nick to the user model'
    return User(**user.model_dump())
