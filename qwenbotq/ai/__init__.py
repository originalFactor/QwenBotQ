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

"AI助手模块"


# Standard imports
from math import ceil
from typing import Annotated
from urllib.error import HTTPError
from collections.abc import Sequence

# Nonebot imports
from nonebot import on_message, on_command
from nonebot.rule import to_me
from nonebot.params import EventPlainText
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.adapters.onebot.v11.event import Reply

# Local imports
from .. import config
from ..database import User
from ..bot_utils import (
    require,
    get_flow_replies,
    arg_plain_text,
    arg,
)
from .tools import get_sysprompt, construct_history, tokenize
from .core import chat


# 大模型回复匹配器
LLMMatcher = on_message(to_me(), priority=20)


@LLMMatcher.handle()
async def llm(
    user: Annotated[User, require()],
    prompt: Annotated[str, EventPlainText()],
    replies: Annotated[Sequence[Reply] | None, get_flow_replies],
    bot: Bot,
    event: MessageEvent,
):
    "大模型回复"

    # 检查模型是否可用
    if user.model not in config.models.keys():
        await user.set({User.model: list(config.models.keys())[0]})
        await LLMMatcher.send(
            f"\n您所选模型已下线，已自动为您切换可用的 {config.models[user.model].name} 模型",
            at_sender=True,
        )

    # 检查是否有提示词
    if not prompt:
        await LLMMatcher.finish("\n虽然你啥也没说，但是我记住你了！", at_sender=True)

    # 构建历史消息
    system_prompt = get_sysprompt(user.system_prompt)
    messages = construct_history(replies or [], int(bot.self_id))
    messages.append({"role": "user", "content": prompt})

    # 扣费白名单
    free = user.permission or (isinstance(event, GroupMessageEvent) and event.group_id in config.ai_vip_groups)

    # 成本控制
    model = config.models[user.model]
    predicted_tokens = tokenize(messages)
    predicted_coins = ceil(
        predicted_tokens * model.input_cost / 1000 + model.output_cost
    )
    if not free and predicted_coins > user.coins:
        await LLMMatcher.finish(
            f"\n输入上下文大小 {predicted_tokens} tokens 已超过积分余额所能负担的最大值。",
            at_sender=True,
        )

    # 检查上下文长度是否足够
    if predicted_tokens > (model.context_length or float("inf")):
        await LLMMatcher.finish(
            f"\n上下文长度 {predicted_tokens} tokens 超过模型能够处理的最长长度 {model.context_length} tokens",
            at_sender=True,
        )

    # 流式回复track
    usage_after: int = 0
    reply_id = event.message_id
    session_id = (
        f"g{event.group_id}"
        if isinstance(event, GroupMessageEvent)
        else f"u{event.user_id}"
    )

    try:
        async for paragraph in chat(
            user.model,
            system_prompt,
            messages,
            user.temprature,
            user.frequency_penalty,
            user.presence_penalty,
            session_id,
        ):
            data = await LLMMatcher.send(
                MessageSegment.reply(reply_id) + paragraph.paragraph
            )
            reply_id = data["message_id"]
            usage_after = 0 if free else paragraph.cost
        await LLMMatcher.finish(
            MessageSegment.reply(reply_id) + f"\u200b 共消耗 {usage_after} 积分。"
        )
    except HTTPError as e:
        await LLMMatcher.finish(MessageSegment.reply(reply_id) + f"上游异常：{e}")

    LLMMatcher.finish(MessageSegment.reply(reply_id) + f"内部异常。")


# 设置系统提示词匹配器
PromptMatcher = on_command("设置系统提示词", block=True)


@PromptMatcher.handle()
async def set_prompt(
    user: Annotated[User, require(0, config.set_prompt_cost)],
    prompt: Annotated[str, arg_plain_text],
):
    "设置系统提示词"
    await user.set({User.system_prompt: prompt})
    await PromptMatcher.finish("\n已尝试更新您的专属系统提示词", at_sender=True)


# 更换模型匹配器
ModelChangeMatcher = on_command("更改模型", block=True)


@ModelChangeMatcher.handle()
async def model_change(
    user: Annotated[User, require()], args: Annotated[str, arg_plain_text]
):
    "更改模型"
    if not args or args not in config.models:
        await ModelChangeMatcher.finish(
            "\n请指定一个正确的目标模型。\n支持的模型：\n\n"
            + (
                "\n\n".join(
                    [
                        f"ID: {_[0]}\n"
                        f"名称: {_[1].name}\n"
                        f"输入消耗倍率：{_[1].input_cost}\n"
                        f"输出消耗倍率：{_[1].output_cost}\n"
                        f"最大上下文长度：{_[1].context_length}\n"
                        f"最长输出长度：{_[1].max_tokens} token\n"
                        f"简介：{_[1].detail}"
                        for _ in config.models.items()
                    ]
                )
            )
            + "\n\n注：消耗计算方式：接口给出的消耗Token数/1000*倍率，消耗积分。",
            at_sender=True,
        )
    await user.set({User.model: args})
    await ModelChangeMatcher.finish("\n成功为您更换模型。", at_sender=True)


# 设置模型参数
ConfMatcher = on_command("设置参数", block=True)


@ConfMatcher.handle()
async def conf(
    user: Annotated[User, require()],
    args: Annotated[tuple[str, float], arg((str, float))],
):
    key, val = args
    if key == "温度":
        key = "temprature"
    elif key == "频率惩罚":
        key = "frequency_penalty"
    elif key == "重复惩罚":
        key = "presence_penalty"
    else:
        await ConfMatcher.finish("请输入合法的参数名", at_sender=True)
    await user.set({key: val})
    await ConfMatcher.finish("已尝试设定", at_sender=True)


# 隐藏消耗积分匹配器
HideUsageMatcher = on_command("切换消耗显示", block=True)


@HideUsageMatcher.handle()
async def hide_usage(
    user: Annotated[User, require()],
    args: Annotated[Sequence[bool], arg(bool)],
):
    "隐藏消耗积分"
    hide_usage = (
        args[0] if args and args[0] is not None else not (user.hide_usage or False)
    )
    await user.set({User.hide_usage: hide_usage})
    await HideUsageMatcher.finish(
        message=f"已尝试设定隐藏消耗积分为 {'启用' if hide_usage else '禁用'}",
        at_sender=True,
    )
