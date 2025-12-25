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

SYSPROMPT_APPEND = """
注意：
1. 你是一个聊天机器人，你的回复应该较简短，符合即时通讯的需求。
2. 你可以通过双换行分段，分段后该段落会被提前发送。你可以用分段的方式来发送较长的内容而避免用户等待过长时间。
3. 因此你应该避免在应连续的内容中插入双换行，导致奇怪的分段效果。你可以通过在两个换行间插入 `\\~` 来避免这个问题，例如 `\\n\\~\\n` 。
"""


# Standard imports
import asyncio
from math import ceil
from typing import Annotated, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError

# OpenAI imports
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk

# Nonebot imports
from nonebot import logger, on_message, on_command
from nonebot.params import EventPlainText
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.event import Reply

# Local imports
from . import config
from .database import User
from .bot_utils import (
    require,
    get_flow_replies,
    strict_to_me,
    arg_plain_text,
    arg,
)

# Tiktoken imports
if not config.fast_tokenize:
    from tiktoken import encoding_for_model, get_encoding

openai = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)


# 分词
def tokenize(model: str, messages: Sequence[Mapping[str, str]]) -> int:
    if config.fast_tokenize:
        return sum(len(_["content"]) + 4 for _ in messages)
    try:
        encoding = encoding_for_model(model)  # type: ignore
    except KeyError:
        encoding = get_encoding("cl100k_base")  # type: ignore
    return sum(len(encoding.encode(_["content"])) + 4 for _ in messages)


# 大模型回复匹配器
LLMMatcher = on_message(strict_to_me, priority=20)


@LLMMatcher.handle()
async def llm(
    user: Annotated[User, require()],
    prompt: Annotated[str, EventPlainText()],
    replies: Annotated[Optional[Sequence[Reply]], get_flow_replies],
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
    user.system_prompt = (
        config.system_prompt if user.system_prompt == "DEFAULT" else user.system_prompt
    )
    messages = [{"role": "system", "content": user.system_prompt + SYSPROMPT_APPEND}]
    if replies:
        last_role: str | None = None
        for r in replies:
            content = r.message.extract_plain_text().rsplit("-(", 1)[0].strip()
            if not content:
                continue
            if content.startswith("\u200b"):
                continue
            role = "assistant" if r.sender.user_id == int(bot.self_id) else "user"
            if last_role == role:
                messages[-1]["content"] += "\n\n" + content
                continue
            messages.append({"role": role, "content": content})
            last_role = role
    messages.append({"role": "user", "content": prompt})

    # 成本控制
    if (
        ceil(
            usage := ceil(
                tokenize(user.model, messages)
                if (_ := config.models[user.model].input_cost)
                else 0
            )
            / 1000
            * _
        )
        + config.models[user.model].output_cost
        > user.coins
    ):
        await LLMMatcher.finish(
            f"\n输入上下文大小 {usage} tokens 已超过积分余额所能负担的最大值。",
            at_sender=True,
        )

    # 检查上下文长度是否足够
    if _ := config.models[user.model].context_length:
        if usage > _:
            await LLMMatcher.finish(
                "\n上下文长度超过模型能够处理的最长长度", at_sender=True
            )

    # 流式回复track
    received: str = ""
    received_debug: str = ""
    usage_after: int = 0
    received_len: int = 0
    reply_id = event.message_id

    try:
        # 创建请求
        response: AsyncStream[ChatCompletionChunk] = (
            await openai.chat.completions.create(
                model=user.model,
                messages=messages,  # type: ignore
                max_tokens=config.models[user.model].max_tokens,
                temperature=user.temprature,
                frequency_penalty=user.frequency_penalty,
                presence_penalty=user.presence_penalty,
                stream=True,
            )
        )

        # 处理回复
        assert isinstance(response, AsyncStream)
        async for chunk in response:
            assert isinstance(chunk, ChatCompletionChunk)
            # 更新用量
            if chunk.usage:
                usage_after = ceil(
                    chunk.usage.prompt_tokens
                    / 1000
                    * config.models[user.model].input_cost
                    + chunk.usage.completion_tokens
                    / 1000
                    * config.models[user.model].output_cost
                )
            # 有数据
            if not chunk.choices[0].delta.content:
                continue
            # 加入数据
            received += (delta := chunk.choices[0].delta.content)
            received_debug += delta
            # 寻找段落分隔符
            paras = received[received_len - 1 :].split("\n\n")
            paras[0] = received[: received_len - 1] + paras[0]
            received_len = len(received)
            if len(paras) <= 1:
                continue
            # 发送段落
            for para in paras[:-1]:
                res: dict = await LLMMatcher.send(
                    MessageSegment.reply(reply_id) + para.replace("\\~", "").strip(),
                )
                reply_id = int(res.get("message_id", reply_id))

            # 删除段落
            received = paras[-1]
            received_len = len(received)

        if received:
            res = await LLMMatcher.send(
                MessageSegment.reply(reply_id) + received.replace("\\~", "").strip(),
            )
            reply_id = int(res.get("message_id", reply_id))

        await user.inc({User.coins: -usage_after})
        logger.info(f"FULL CONTENT: {received_debug}")

        await asyncio.sleep(0.5)
        if not user.hide_usage:
            await LLMMatcher.finish(
                MessageSegment.reply(reply_id) + f"\u200b已消耗 {usage_after} 积分。"
            )
        await LLMMatcher.finish()
    except HTTPError as e:
        await LLMMatcher.finish(f"\n错误：{e}", at_sender=True)
    await LLMMatcher.finish(
        "\n服务器返回无效：" + response.model_dump_json(), at_sender=True
    )


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
    args: Annotated[Tuple[str, float], arg((str, float))],
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
