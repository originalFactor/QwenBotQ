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

"The global initialize module of QwenBotQ."

from nonebot import on_command
from .bot_utils import strict_to_me
from nonebot.permission import SUPERUSER
from .database import initialize_database

# 初始化机器人，需要配置文件超管权限
InitMatcher = on_command('删库跑路', strict_to_me,
                         permission=SUPERUSER, block=True)


@InitMatcher.handle()
async def initialize():
    '`删库跑路`命令handler'
    await initialize_database()
    await InitMatcher.finish('\n已尝试初始化数据库。', at_sender=True)

# 指南
HelpMatcher = on_command('说明书', block=True)


@HelpMatcher.handle()
async def help_message():
    '`说明书`命令handler'
    await HelpMatcher.finish(
        "\n欢迎使用QQ娱乐机器人！\n"
        "请查看官方命令指南：\n"
        "http://qwenbotq.us.to/#/help/\n"
        "如命令发送后无反应可能是您的积分不足或权限过低。",
        at_sender=True
    )
