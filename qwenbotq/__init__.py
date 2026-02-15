# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"QwenBotQ 主要部分"

from ssl import PROTOCOL_TLS_CLIENT
from importlib import import_module

from truststore import SSLContext
from httpx import AsyncClient
from nonebot import get_driver, require

httpClient = AsyncClient(verify=SSLContext(PROTOCOL_TLS_CLIENT))
driver = get_driver()

from .config_model import get_config

config = get_config()

if config.focus or config.lottery:
    require("nonebot_plugin_apscheduler")

require("nonebot_plugin_alconna")

import_module(".binding", __package__)
import_module(".usersystem", __package__)

if config.ai:
    import_module(".ai", __package__)

    if config.ai.memory:
        import_module(".ai.memory", __package__)

if config.focus:
    import_module(".bilinotice", __package__)

if config.lottery:
    import_module(".lottery", __package__)


# 帮助命令
from arclet.alconna import Alconna
from nonebot_plugin_alconna import on_alconna

HELP_TEXT = (
    "QwenBotQ 命令列表\n"
    "\n"
    "【用户系统】\n"
    "  签到 — 每日签到领取积分\n"
    "  用户信息 [@用户] — 查看用户信息\n"
    "  转账给 @用户 <积分数量> — 转账积分\n"
    "\n"
    "【绑定系统】\n"
    "  今日老公 — 随机绑定今日老公\n"
    "  换老公 — 解除当前绑定\n"
    "  续期 — 续期当前绑定关系\n"
)

if config.ai:
    HELP_TEXT += (
        "\n"
        "【AI 助手】\n"
        "  @我 <消息> — 与 AI 对话\n"
        "  设置系统提示词 <名称> — 切换智能体\n"
        "  更改模型 [模型ID] — 切换 AI 模型\n"
        "  会话信息 — 查看当前会话状态\n"
        "  添加智能体 <名称> <提示词> [选项] — 添加智能体\n"
        "  删除智能体 <名称> — 删除智能体（管理员）\n"
        "  修改智能体 <名称> [选项] — 修改智能体属性（管理员）\n"
    )
    if config.ai.memory:
        HELP_TEXT += "  清除记忆 — 清除当前会话记忆\n" "  查看记忆 — 查看当前会话记忆\n"

if config.focus:
    HELP_TEXT += "\n" "【订阅】\n" "  相关订阅命令请查看文档\n"

if config.lottery:
    HELP_TEXT += (
        "\n"
        "【抽奖】\n"
        "  购买奖号 <6位数字> — 花费积分购买奖号\n"
        "  我的奖号 — 查看待开奖的奖号\n"
        "  每天中午12:00自动开奖\n"
    )

HELP_TEXT += (
    "\n"
    "【管理】\n"
    "  续期vip <会话ID> <天数> — 续期 AI VIP（管理员）\n"
    "\n"
    "发送 帮助 查看此信息"
)

HelpMatcher = on_alconna(Alconna("帮助"), block=True)


@HelpMatcher.handle()
async def show_help():
    await HelpMatcher.finish(f"\n{HELP_TEXT}", at_sender=True)
