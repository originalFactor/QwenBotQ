# Copyright (C) 2025 originalFactor
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

from typing import Annotated

from nonebot import on_message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.params import Depends
from nonebot.adapters.onebot.v11 import MessageEvent

from . import config

last_call: dict[int, list[str]] = {}
max_size = 128

async def getkw(event: MessageEvent) -> list[str]:
    if id(event) in last_call:
        return last_call[id(event)]
    ans: list[str] = []
    uid = event.get_user_id()
    msg = event.get_plaintext()
    if uid in config.keywords:
        ans += [r for k, r in config.keywords[uid] if k in msg]
    if 'global' in config.keywords:
        ans += [r for k, r in config.keywords['global'] if k in msg]
    last_call[id(event)] = ans
    if len(last_call) > max_size:
        last_call.pop(next(iter(last_call)))
    return ans

async def getkw_match(event: MessageEvent) -> bool:
    return bool(await getkw(event))

@on_message(rule=Rule(getkw_match)).handle()
async def handle_keyword(m: Matcher, r: Annotated[list[str], Depends(getkw)]):
    await m.finish("\n\n".join(r), at_sender=True)