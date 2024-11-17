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

from http import HTTPStatus
from math import ceil
from typing import Annotated, Mapping, Optional, Sequence
from urllib.error import HTTPError
from dashscope import AioGeneration, Tokenization
from dashscope.api_entities.dashscope_response import GenerationResponse
from nonebot import on_message, on_command
from nonebot.log import logger
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


async def tokenize(model: str, messages: Sequence[Mapping[str, str]])->int:
    if _ := Tokenization.call(model, messages=messages, api_key=config.api_key).usage:
        return _['input_tokens']
    else:
        logger.warning('分词失败，正在忽略输入消耗……')
        return 0

# 大模型回复匹配器
LLMMatcher = on_message(strict_to_me, priority=20)

@LLMMatcher.handle()
async def llm(
        user: Annotated[User, require()],
        prompt: Annotated[str, EventPlainText()],
        replies: Annotated[Optional[Sequence[Reply]], get_flow_replies],
        bot: Bot
):
    "大模型回复"
    if user.model not in config.models.keys():
        await user.set({User.model: list(config.models.keys())[0]})
        await LLMMatcher.send(
            f'\n您所选模型已下线，已自动为您切换可用的 {config.models[user.model].name} 模型',
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
        
        
        if ceil(
            (usage := await tokenize(user.model, messages))
            /1000 * config.models[user.model].input_cost
            +
            config.models[user.model].output_cost
        ) > user.coins:
            await LLMMatcher.finish(
                f'\n输入上下文大小 {usage} tokens 已超过积分余额所能负担的最大值。',
                at_sender=True
            )
        if config.models[user.model].max_tokens is not None:
            if usage > config.models[user.model].max_tokens:
                await LLMMatcher.finish(
                    '\n上下文长度超过模型能够处理的最长长度',
                    at_sender=True
                )
        try:
            response: GenerationResponse = await AioGeneration.call(
                user.model,
                api_key=config.api_key,
                messages=messages,
                result_format='message',
                enable_search=True
            )
        except HTTPError as e:
            await LLMMatcher.finish(
                f"\n错误：{e}",
                at_sender=True
            )
        if response.status_code == HTTPStatus.OK:
            usage = ceil(
                response.usage.input_tokens/1000*config.models[user.model].input_cost
                +
                response.usage.output_tokens/1000*config.models[user.model].output_cost
            )
            await user.inc({User.coins: -usage})
            await LLMMatcher.finish(
                response.output.choices[0].message.content+'\n'
                f'-( 本次共消耗{usage}积分 )-',
                reply_message=True
            )
        await LLMMatcher.finish(
            f'\n服务器返回异常状态码 {response.status_code}，详情：\n'
            f'请求ID: {response.request_id}\n'
            f'错误代码：{response.code}\n'
            f'错误详情：{response.message}',
            at_sender=True
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
            '\n请指定一个正确的目标模型。\n支持的模型：\n\n'+
            ('\n\n'.join([
                f'ID: {_[0]}\n'
                f'名称: {_[1].name}\n'
                f'输入消耗倍率：{_[1].input_cost}\n'
                f'输出消耗倍率：{_[1].output_cost}\n'
                f'最长输入长度：{_[1].max_tokens} token\n'
                f'简介：{_[1].detail}'
                for _ in config.models.items()
            ]))+
            '\n\n注：消耗计算方式：接口给出的消耗Token数/1000*倍率，消耗积分。',
            at_sender=True
        )
    await user.set({User.model: args})
    await ModelChangeMatcher.finish(
        '\n成功为您更换模型。',
        at_sender=True
    )
