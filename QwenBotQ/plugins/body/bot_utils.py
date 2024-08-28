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

'''
供主体使用的Bot实用函数
'''

from typing import Tuple, Union, Annotated
from enum import Enum
from datetime import datetime
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Sender
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from pydantic import BaseModel
from .database import User, NickCache, use_nick, find_nick, update_user, get_user, UserWithNick


async def nick(user: User, bot: Bot) -> str:
    "获取用户昵称"

    if not (_ := await find_nick(user.id)):
        _ = NickCache(
            id=user.id,
            nick=(await bot.get_stranger_info(
                user_id=int(user.id)
            ))['nickname'],
            created=datetime.now()
        )
        await use_nick(_)
    return _.nick


async def u2uwn(user: User, bot: Bot) -> UserWithNick:
    "将User模型转换为UserWithNick模型"
    return UserWithNick(**user.model_dump(), nick=await nick(user, bot))


def require(cost_permission: int = 0, cost_coins: int = 0):
    "用于获取发送用户的权限函数，可指定最小权限等级以及消耗积分数量"
    @Depends
    async def _require(event: MessageEvent, matcher: Matcher, bot: Bot) -> UserWithNick:
        user = await get_user(event.user_id)
        if user.permission < cost_permission:
            await matcher.finish(
                f"\n您的权限不足，至少需要{cost_permission}。",
                at_sender=True
            )
        if cost_coins:
            if user.coins < cost_coins:
                await matcher.finish(
                    f"\n您的积分不足，至少需要{cost_coins}。",
                    at_sender=True
                )
            user.coins -= cost_coins
            await update_user(user)
            await matcher.send(
                f"\n您已被扣除所需的{cost_coins}点积分！",
                at_sender=True
            )
        return await u2uwn(await get_user(event.user_id), bot)
    return _require


@Depends
async def arg_plain_text(args: Annotated[Message, CommandArg()]) -> str:
    '获取命令纯文本参数'
    return args.extract_plain_text()


def arg(tp: type, least: int = 0):
    "获取至少least个tp类型的命令参数"
    @Depends
    async def _arg(
            matcher: Matcher,
            args: Annotated[str, arg_plain_text]
    ) -> Tuple[tp]:
        try:
            if len(x := tuple(map(tp, args.strip().split()))) >= least:
                return x
            await matcher.finish(
                f'请输入至少{least}个{tp}类型参数！',
                at_sender=True
            )
        except ValueError:
            await matcher.finish(
                f'\n请输入合法的{tp}类型参数！',
                at_sender=True
            )
    return _arg


def mentioned(least: int = 0):
    "获取至少least个被提及的用户"
    @Depends
    async def _mentioned(
        matcher: Matcher,
        bot: Bot,
        args: Annotated[Message, CommandArg()]
    ) -> Tuple[UserWithNick, ...]:
        mentioned_users = tuple([
            await u2uwn(await get_user(_.data['qq']), bot) for _ in args['at']
        ])
        if len(mentioned_users) >= least:
            return mentioned_users
        await matcher.finish(
            f'\n该功能至少要提及{least}个用户。',
            at_sender=True
        )
    return _mentioned


class MessageType(str, Enum):
    "消息类型"

    PRIVATE = "private"
    GROUP = "group"


class GetMsgResult(BaseModel):
    "get_msg API的返回模型"

    time: int
    message_type: MessageType
    message_id: int
    real_id: int
    sender: Sender
    message: Message


def reply(required: bool = False):
    "The dependency for replied message"
    @Depends
    async def _reply(
            matcher: Matcher,
            bot: Bot,
            event: MessageEvent) -> Union[GetMsgResult, None]:
        if required and not event.original_message['reply']:
            await matcher.finish(
                "\n必须回复一条消息才能使用此功能",
                at_sender=True
            )
        return (
            GetMsgResult(
                **(
                    await bot.get_msg(
                        message_id=event.original_message['reply',
                                                          0].data['id']
                    )
                )
            )
            if event.original_message['reply']
            else None
        )
    return _reply
