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

'Models'

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, field_validator


class User(BaseModel):
    'The user model of QwenBotQ'

    id: str
    nick: str = ''
    nick_expire: datetime = datetime(1970, 1, 1)
    permission: int = 0
    system_prompt: str = ''
    coins: int = 0
    sign_expire: datetime = datetime(1970, 1, 1)
    avatar: bytes = b''
    avatar_expire: datetime = datetime(1970, 1, 1)


class Couple(BaseModel):
    'The couple model of QwenBotQ'
    A: str
    B: str
    expire: datetime

    @field_validator('expire', mode='before')
    @classmethod
    def autofill_expire(cls, v: Optional[datetime]) -> datetime:
        return v if v else datetime.now()+timedelta(1)


class NickCache(BaseModel):
    'The nick cache model of QwenBotQ'
    id: str
    nick: str
    created: datetime


class UserWithNick(User):
    'The user model with nick'
    nick: str


class Request(BaseModel):
    'Marry request'
    from_user: str
    to_user: str
    expire: datetime

    @ field_validator('expire', mode='before')
    @ classmethod
    def autofill_expire(cls, v: Optional[datetime]) -> datetime:
        'Autofill expiration date if it is not exist'
        return v if v else datetime.now()+timedelta(1)
