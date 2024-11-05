# Copyright (C) 2024 OriginalFactor
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

'一些额外的模型'

from datetime import datetime
from pydantic import BaseModel, field_validator


class EssenceMessage(BaseModel):
    '精华消息模型'
    sender_id: str
    sender_nick: str
    sender_time: datetime
    operator_id: str
    operator_nick: str
    operator_time: datetime
    message_id: int

    @field_validator('sender_id', 'operator_id', mode='before')
    @classmethod
    def validate_id(cls, v:int) -> str:
        '校验id'
        return str(v)

    @field_validator('sender_time', 'operator_time', mode='before')
    @classmethod
    def validate_time(cls, v:int) -> datetime:
        '校验日期'
        return datetime.fromtimestamp(v)
