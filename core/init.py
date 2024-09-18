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

from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11 import FriendRequestEvent, Bot

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


RequestMatcher = on_request()


@RequestMatcher.handle()
async def process_friend_request(event: FriendRequestEvent, bot: Bot):
    '自动同意好友请求'
    await event.approve(bot)
    await RequestMatcher.finish()
