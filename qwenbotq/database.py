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
from typing import List, Union, Annotated, Optional
from datetime import datetime, timedelta

# third-party import
from httpx import HTTPError
from motor.motor_asyncio import AsyncIOMotorClient
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot
from pydantic import BaseModel, Field, ConfigDict
from pymongo import MongoClient

# local import
from . import config, http_client

# Database Client Initialize
database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]
users = database['users']
couples = database['couples']


class User(BaseModel):
    'The user model of QwenBotQ'

    id: Annotated[str, Field(alias='_id')]
    permission: int = 0
    system_prompt: str = config.system_prompt
    coins: int = 0
    sign_expire: datetime = datetime(1970, 1, 1)
    nick:str = 'Unknown'
    avatar: bytes = b''
    model:str = list(config.models.keys())[0]
    profile_expire: datetime = datetime(1970, 1, 1)

    @classmethod
    async def min_get(cls, id: Union[str,int])->'User':
        'Get user from database'
        user = cls.model_validate(_ if (_:=await users.find_one({'_id':str(id)})) else {'_id':str(id)})
        if not _: await user.write()
        return user

    @classmethod
    async def get(cls, id: Union[str,int], bot:Bot) -> 'User':
        'Get user from database'
        doc = await cls.min_get(id)
        if doc.profile_expire < datetime.now():
            doc.nick = (await bot.get_stranger_info(user_id=int(id)))['nickname']
            try:
                resp = await http_client.get(f'https://q.qlogo.cn/g?b=qq&nk={id}&s=640')
                resp.raise_for_status()
            except HTTPError as e:
                logger.warning(f'Failed to get avatar of user {id}: {e}\n\tUsing empty avatar.')
            else:
                doc.avatar = resp.content
            doc.profile_expire = datetime.now() + timedelta(1)
            await doc.update()
        return doc

    async def remove(self):
        'Remove user from database'
        await users.delete_many({'_id': self.id})

    async def write(self):
        'Write user to database'
        await self.remove()
        await users.insert_one(self.model_dump(by_alias=True))

    async def update(self):
        'Update user to database'
        await users.update_one(
            {'_id': self.id},
            {'$set': self.model_dump(by_alias=True)}
        )

    @property
    async def couple(self)->Optional['CoupleInfo']:
        'Get the couple user'
        return await CoupleInfo.get(self.id)

    class Config:
        by_alias = True


class Couple(BaseModel):
    'The couple model of QwenBotQ'
    A: str
    B: str
    expire: datetime

    @classmethod
    async def get(cls, id: Union[str,int])->Optional['Couple']:
        'Get couple from database'
        return cls.model_validate(_) if (_:=await couples.find_one({'$or':[{'A':str(id)}, {'B':str(id)}]})) else None

    @classmethod
    async def _delete(cls, id: Union[str,int]):
        'Delete couples from database'
        await couples.delete_many({'$or':[{'A':str(id)}, {'B':str(id)}]})

    async def delete(self):
        'Delete this couple from database'
        await self._delete(self.A)
        await self._delete(self.B)

    async def apply(self):
        await self.delete()
        await couples.insert_one(self.model_dump(by_alias=True))

    async def update(self):
        await couples.update_one(
            {'$or':[{'A':self.A},{'B':self.B}]},
            {'$set': self.model_dump(by_alias=True)}
        )

class CoupleInfo(BaseModel):
    user: User
    expire: datetime

    @classmethod
    async def get(cls, id: Union[str,int])->Optional['CoupleInfo']:
        'Get couple info from database'
        return cls.model_validate({
            'user': await User.min_get(cp.B if cp.A == str(id) else cp.A),
            'expire': cp.expire
        }) if (cp := await Couple.get(id)) else None

async def get_top10_users() -> List[User]:
    'Get the top 10 users sorted by coins'
    result = []
    async for document in users.find({}).sort('coins', -1).limit(10):
        result.append(User.model_validate(document))
    return result

# Database initialization
client = MongoClient(config.mongo_uri)[config.mongo_db]
for superuser in config.supermgr_ids:
    if not client['users'].find_one({'_id': superuser}):
        client['users'].insert_one(User.model_validate({'_id': superuser, 'permission': 3}).model_dump(by_alias=True))
index_info = client['couples'].index_information()
if 'A' not in index_info:
    client['couples'].create_index(['A'], unique=True)
if 'B' not in index_info:
    client['couples'].create_index(['B'], unique=True)