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
from typing import Iterable, Optional, Union, Tuple
from datetime import datetime, timedelta
from os.path import isdir, split, isfile
from os import mkdir, listdir, remove
from asyncio import run
# third-party import
from pydantic import BaseModel, field_validator
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient, HTTPError
from nonebot import logger
from pymongo import IndexModel
# local import
from . import config, version
from .utils import still_valid


# Global assignments
http_client = AsyncClient()

database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]

users = database['users']
couples = database['couples']
nicks = database['nicks']
requests = database['requests']

# Initialize


async def initialize():
    'Initialize the database.'
    await users.drop_indexes()
    updated_superusers = [
        User(id=_, permission=999).model_dump()
        for _ in config.supermgr_ids
        if not await users.find_one({'id': _})
    ]
    if updated_superusers:
        await users.insert_many(updated_superusers)
    await users.create_index('id', unique=True)
    await couples.drop_indexes()
    await couples.create_indexes([
        IndexModel(['A'], unique=True),
        IndexModel(['B'], unique=True)
    ])
    await nicks.drop_indexes()
    await nicks.create_index('id', unique=True)
    await requests.drop_indexes()
    await requests.create_indexes([
        IndexModel(['from_user'], unique=True),
        IndexModel(['to_user'], unique=True)
    ])
if not isfile('db.ver') or \
        ((_ := open('db.ver', encoding='utf-8')).read() != version and not _.close()):
    run(initialize())
    with open('db.ver', 'w', encoding='utf-8') as _:
        _.write(version)

# Models


# Functions to process database with models


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


async def get_top10_users() -> Tuple[User]:
    'Get the top 10 users sorted by coins'
    result = []
    async for document in users.find({}).sort('coins', -1).limit(10):
        result.append(User(**document))
    return tuple(result)


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


async def uwn2u(user: Union[User, UserWithNick]) -> User:
    'Convert the user model with nick to the user model'
    return User.model_validate(user.model_dump()) if isinstance(user, UserWithNick) else user


async def remove_request(*binded_users: Iterable[str]):
    'Remove old marry requests'
    for user in binded_users:
        await requests.delete_many({
            '$or': [
                {'from_user': user},
                {'to_user': user}
            ]
        })


async def send_request(request: Request):
    'Send new marry request'
    await remove_request(request.from_user, request.to_user)
    await requests.insert_one(request.model_dump())


async def approve_request(user: str):
    'Approve marry request'
    req = Request.model_validate(await requests.find_one({'to_user': user}))
    await use_couple(
        Couple(
            A=req.from_user,
            B=req.to_user,
            date=datetime.today()+timedelta(100*365)
        )
    )
