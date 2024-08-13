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

from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent
from asyncio import sleep
from .database import isFirstTime
from . import config

# [TO ME] `/init`
init = on_command('init',to_me(),permission=SUPERUSER)
@init.handle()
async def checkInit(event:GroupMessageEvent):
    await isFirstTime()
    await init.finish(MessageSegment.at(event.user_id)+'\n已尝试初始化数据库。')

# [TO ME] `/help`
help = on_command('help')
@help.handle()
async def helpMsg(event:GroupMessageEvent, bot:Bot):
    await help.finish(
        MessageSegment.at(event.user_id)+
        "\n欢迎使用QQ娱乐机器人！\n"
        "请查看官方命令指南：\n"
        "http://qwenbotq.us.to/#/help/"
    )
