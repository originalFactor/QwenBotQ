# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from nonebot import on_command

HELP_TEXT = "QwenBotQ 命令列表"

HelpMatcher = on_command("帮助", block=True)


@HelpMatcher.handle()
async def show_help():
    await HelpMatcher.finish(f"\n{HELP_TEXT}", at_sender=True)
