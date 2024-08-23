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
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from .database import initialize_database

# [TO ME] `/init`
InitMatcher = on_command('init', to_me(), permission=SUPERUSER)


@InitMatcher.handle()
async def initialize():
    'Initialize the database. Handle `/init` command.'
    await initialize_database()
    await InitMatcher.finish('\n已尝试初始化数据库。', at_sender=True)

# [TO ME] `/help`
HelpMatcher = on_command('help')


@HelpMatcher.handle()
async def help_message():
    'Handle `/help` command.'
    await HelpMatcher.finish(
        "\n欢迎使用QQ娱乐机器人！\n"
        "请查看官方命令指南：\n"
        "http://qwenbotq.us.to/#/help/",
        at_sender=True
    )
