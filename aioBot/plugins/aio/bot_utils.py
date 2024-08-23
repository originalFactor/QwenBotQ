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
The utils for bot.py to use.
'''

from typing import Union, Annotated, List
from enum import Enum
from datetime import datetime
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Sender
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from pydantic import BaseModel
from .database import User, NickCache, use_nick, find_nick, update_user, get_user, UserWithNick


async def nick(user: User, bot: Bot) -> str:
    "Get the nick of user"

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

# convert user into userwithnick


async def u2uwn(user: User, bot: Bot) -> UserWithNick:
    "Convert User into UserWithNick"
    return UserWithNick(**user.model_dump(), nick=await nick(user, bot))


def require(cost_permission: int = 0, cost_coins: int = 0):
    "The dependency for to get user"
    async def _require(matcher: Matcher, event: MessageEvent, bot: Bot) -> UserWithNick:
        user = await get_user(event.user_id)
        if user.permission < cost_permission:
            await matcher.finish(
                f'\n你的权限等级不足，需要{cost_permission}以上才能使用本功能',
                at_sender=True
            )
        if cost_coins:
            if user.coins < cost_coins:
                await matcher.finish(
                    f'\n你的积分不足，需要至少{cost_coins}积分才能使用本功能',
                    at_sender=True
                )
            user.coins -= cost_coins
            await update_user(user)
            await matcher.send(
                f'\n你已被扣除{cost_coins}点积分以使用本功能',
                at_sender=True
            )
        return await u2uwn(user, bot)
    return _require


def arg(tp: type):
    "The dependency for command argument in `tp` type"

    async def _arg(
            matcher: Matcher,
            args: Annotated[Message, CommandArg()]
    ) -> tp:
        try:
            return tp(args.extract_plain_text().strip())
        except ValueError:
            await matcher.finish(
                f'\n请输入合法的{tp}类型参数！',
                at_sender=True
            )
    return _arg


def mentioned(least: int = 0):
    "The dependency for mentioned users"

    async def _mentioned(
        matcher: Matcher,
        bot: Bot,
        args: Annotated[Message, CommandArg()]
    ) -> List[UserWithNick]:
        mentioned_users = list([await u2uwn(await get_user(_.data['qq']), bot) for _ in args['at']])
        if len(mentioned_users) < least:
            await matcher.finish(
                f'\n该功能至少要提及{least}个用户。',
                at_sender=True
            )
        return mentioned_users
    return _mentioned


class MessageType(str, Enum):
    "The type of message"

    PRIVATE = "private"
    GROUP = "group"


class GetMsgResult(BaseModel):
    "The result of bot.get_msg"

    time: int
    message_type: MessageType
    message_id: int
    real_id: int
    sender: Sender
    message: Message


def reply(required: bool = False):
    "The dependency for replied message"
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
