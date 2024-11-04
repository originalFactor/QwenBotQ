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
from typing import List, Annotated, Optional, Dict
from datetime import datetime, time

# third-party import
from motor.motor_asyncio import AsyncIOMotorClient
from nonebot.adapters.satori import Bot
from nonebot.adapters.satori.models import User as SatoriUser
from pydantic import BaseModel, Field, field_validator
from pymongo import MongoClient

# local import
from . import config

# Database Client Initialize
database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]
users = database['users']
couples = database['couples']

LOADED_USER_POOL: Dict[str, "StorageUser"] = {}


class StorageUser(BaseModel):
    'The user model of QwenBotQ'

    id: Annotated[str, Field(alias='_id')]
    permission: int = 0
    system_prompt: str = config.system_prompt
    coins: int = 0
    sign_expire: datetime = datetime.min
    model: str = list(config.models.keys())[0]

    @classmethod
    async def get(cls, _id: str):
        'Import data from database'
        if _id in LOADED_USER_POOL:
            return LOADED_USER_POOL[_id]
        user = cls.model_validate(_ if (_ := await users.find_one({'_id': _id})) else {'_id': _id})
        if not _:
            await user.write()
        return user

    async def remove(self):
        'Remove user from database'
        await users.delete_many({'_id': self.id})
        del LOADED_USER_POOL[self.id]

    async def write(self):
        'Write user to database'
        await self.remove()
        await users.insert_one(self.model_dump(by_alias=True))
        LOADED_USER_POOL[self.id] = self

    async def update(self):
        'Update user to database'
        await users.update_one(
            {'_id': self.id},
            {'$set': self.model_dump(by_alias=True)}
        )

    async def couple(self, bot: Bot) -> Optional['CoupleInfo']:
        'Get the couple user'
        return _ \
            if (_ := await CoupleInfo.get(self.id, bot)) and _.expire > datetime.now() \
            else None

    @field_validator('sign_expire', mode="before")
    @classmethod
    def sign_expire_validator(cls, v: datetime) -> datetime:
        '使签到过期使用自然日结算'
        return datetime.combine(v.date(), time.min)


class UserInstanceEmpty(Exception):
    'Exception class for empty user instance'


class User(BaseModel):
    'The combine of StorageUser and SatoriUser'
    fw: SatoriUser = None
    db: StorageUser = None

    async def complete(self, bot: Bot):
        'To auto-complete the instance'
        if not self.fw and self.db:
            self.fw = await bot.user_get(user_id=self.db.id)
        elif not self.db and self.fw:
            self.db = await StorageUser.get(self.fw.id)
        elif self.db and self.fw:
            return
        else:
            raise UserInstanceEmpty()


LOADED_COUPLE_POOL: Dict[str, 'Couple'] = {}


class Couple(BaseModel):
    'The couple model of QwenBotQ'
    A: str
    B: str
    expire: datetime

    @classmethod
    async def get(cls, _id: str) -> Optional['Couple']:
        'Get couple from database'
        if _id in LOADED_COUPLE_POOL:
            return LOADED_COUPLE_POOL[_id]
        return cls.model_validate(_) \
            if (_ := await couples.find_one({'$or': [{'A': str(_id)}, {'B': str(_id)}]})) \
            else None

    @classmethod
    async def _delete(cls, _id: str):
        'Delete couples from database'
        del LOADED_COUPLE_POOL[_id]
        await couples.delete_many({'$or': [{'A': str(_id)}, {'B': str(_id)}]})

    async def delete(self):
        'Delete this couple from database'
        await self._delete(self.A)
        await self._delete(self.B)

    async def apply(self):
        'Make sure it\'s the only one couple and write it to database.'
        await self.delete()
        await couples.insert_one(self.model_dump(by_alias=True))

    async def update(self):
        'Update this couple to database'
        await couples.update_one(
            {'$or': [{'A': self.A}, {'B': self.B}]},
            {'$set': self.model_dump(by_alias=True)}
        )

    @field_validator('expire', mode='before')
    @classmethod
    def expire_validator(cls, v: datetime) -> datetime:
        '使用自然日结算'
        return datetime.combine(v.date(), time.min)


class CoupleInfo(BaseModel):
    'Easier to use couple.'
    user: User
    expire: datetime

    @classmethod
    async def get(cls, _id: str, bot: Bot) -> Optional['CoupleInfo']:
        'Get couple info from database'
        return cls(
            user=await User.get(await bot.user_get(user_id=(cp.B if cp.A == _id else cp.A))),
            expire=cp.expire
        ) if (cp := await Couple.get(_id)) else None


async def get_top10_users(bot: Bot) -> List[User]:
    'Get the top 10 users sorted by coins'
    result = []
    async for document in users.find({}).sort('coins', -1).limit(10):
        user = User(db=StorageUser.model_validate(document))
        await user.complete(bot)
        result.append(user)
    return result

# Database initialization
client = MongoClient(config.mongo_uri)[config.mongo_db]
for superuser in config.supermgr_ids:
    if not client['users'].find_one({'_id': superuser}):
        client['users'].insert_one(User.model_validate(
            {'_id': superuser, 'permission': 3}).model_dump(by_alias=True))
index_info = client['couples'].index_information()
if 'A' not in index_info:
    client['couples'].create_index(['A'], unique=True)
if 'B' not in index_info:
    client['couples'].create_index(['B'], unique=True)
