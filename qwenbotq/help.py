# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from nonebot import on_command


class Help:
    msg: str = "QwenBotQ 命令列表"

    @classmethod
    def get_help(cls) -> str:
        return cls.msg

    @classmethod
    def append_help(cls, msg: str) -> None:
        cls.msg += f"\n\n{msg}"


HelpMatcher = on_command("帮助", block=True)


@HelpMatcher.handle()
async def show_help():
    await HelpMatcher.finish(f"\n{Help.get_help()}", at_sender=True)
