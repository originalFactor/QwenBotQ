# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PrivateMessageEvent


class Help:
    msg: str = "QwenBotQ 命令列表"
    superuser_msg: str = ""  # 仅供超管私聊查看的命令 section

    @classmethod
    def get_help(cls, with_superuser: bool = False) -> str:
        if with_superuser and cls.superuser_msg:
            return cls.msg + cls.superuser_msg
        return cls.msg

    @classmethod
    def append_help(cls, msg: str) -> None:
        cls.msg += f"{msg}"

    @classmethod
    def append_superuser_help(cls, msg: str) -> None:
        cls.superuser_msg += f"{msg}"


HelpMatcher = on_command("帮助", block=True)


@HelpMatcher.handle()
async def show_help(bot: Bot, event: MessageEvent):
    # 仅在超管私聊时展示超管 section
    show_superuser = isinstance(event, PrivateMessageEvent) and await SUPERUSER(
        bot, event
    )
    await HelpMatcher.finish(
        f"\n{Help.get_help(show_superuser)}", at_sender=True
    )
