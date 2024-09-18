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

'Initialize database'

from pymongo import MongoClient
from dotenv import load_dotenv
from core.config import Config
from core.database import
from os import environ

load_dotenv()

config = Config.model_validate(environ)

database = MongoClient(config.mongo_uri)[config.mongo_db]

users = database['users']
couples = database['couples']
nicks = database['nicks']
requests = database['requests']

# Initialize
users.drop_indexes()
updated_superusers = [
    User(id=_, permission=999).model_dump()
    for _ in config.supermgr_ids
    if not users.find_one({'id': _})
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
