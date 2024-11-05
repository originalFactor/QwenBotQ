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

'AI助手模块'

from math import ceil
from typing import Annotated, Optional, Sequence
from urllib.error import HTTPError
from openai import AsyncOpenAI
from nonebot import on_message, on_command
from nonebot.params import EventPlainText
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.event import Reply
from . import config
from .database import User
from .bot_utils import (
    require,
    get_flow_replies,
    strict_to_me,
    arg_plain_text
)
from .utils import sum_tokens

# 初始化OpenAI客户端
openai = AsyncOpenAI(
    api_key=config.api_key,
    base_url=config.base_url
)


# 大模型回复匹配器
LLMMatcher = on_message(strict_to_me, priority=20)

@LLMMatcher.handle()
async def llm(
        user: Annotated[User, require(0,1,True)],
        prompt: Annotated[str, EventPlainText()],
        replies: Annotated[Optional[Sequence[Reply]], get_flow_replies],
        bot: Bot
):
    "大模型回复"
    if user.model not in config.models.keys():
        await user.set({User.model: list(config.models.keys())[0]})
        await LLMMatcher.send(
            f'\n您所选模型已下线，已自动为您切换可用的{user.model}模型',
            at_sender=True
        )
    if prompt:
        messages = [
           {'role': 'system', 'content': user.system_prompt}
        ] + [
           {'role': ('assistant' if _.sender == bot.self_id else 'user'),
            'content': _.message.extract_plain_text()}
           for _ in (replies if replies else [])
        ] + [
           {'role': 'user', 'content': prompt}
        ]
        if sum_tokens(messages) >= config.models[user.model][2]:
            await LLMMatcher.finish(
                '\n上下文长度超过模型能够处理的最长长度',
                at_sender=True
            )
        try:
            response = await openai.chat.completions.create(
                model=user.model,
                messages=messages
            )
        except HTTPError as e:
            await LLMMatcher.finish(
                f"\n错误：{e}",
                at_sender=True
            )
        else:
            usage = ceil(
                response.usage.prompt_tokens/1000*config.models[user.model][0]
                +
                response.usage.completion_tokens/1000*config.models[user.model][1]
            )
            await user.inc({User.coins: -usage})
            await LLMMatcher.finish(
                '\n'+response.choices[0].message.content+'\n'
                f'-( 本次共消耗{usage}积分 )-',
                reply_message=True
            )
    await LLMMatcher.finish(
        "\n虽然你啥也没说，但是我记住你了！",
        at_sender=True
    )

# 设置系统提示词匹配器
PromptMatcher = on_command('设置系统提示词', block=True)

@PromptMatcher.handle()
async def set_prompt(
    user: Annotated[User, require(0, config.set_prompt_cost)],
    prompt: Annotated[str, arg_plain_text]
):
    '设置系统提示词'
    await user.set({User.system_prompt: prompt})
    await PromptMatcher.finish(
        '\n已尝试更新您的专属系统提示词',
        at_sender=True
    )

# 更换模型匹配器
ModelChangeMatcher = on_command('更改模型', block=True)
@ModelChangeMatcher.handle()
async def model_change(
    user: Annotated[User, require()],
    args: Annotated[str, arg_plain_text]
):
    '更改模型'
    if not args or args not in config.models:
        await ModelChangeMatcher.finish(
            '\n请指定一个正确的目标模型。\n支持的模型：\n\t模型\t输入消耗\t输出消耗\t最大上下文\n\t'+
            ('\n\t'.join([
                f'{_[0]}\t{_[1][0]}\t{_[1][1]}\t{_[1][2]}'
                for _ in config.models.items()
            ]))+
            '\n注：消耗计算方式：接口给出的消耗Token数/1000*倍率，消耗积分。',
            at_sender=True
        )
    user.model = args
    await user.set({User.model: args})
    await ModelChangeMatcher.finish(
        '\n成功为您更换模型。',
        at_sender=True
    )
