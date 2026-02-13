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

"""
供主体使用的Bot实用函数
"""

import asyncio
from random import random
from typing import Annotated
from collections.abc import Callable, Awaitable

from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, GroupMessageEvent
from nonebot.adapters.onebot.v11.event import Reply

from . import config
from .database import User, get_vip


async def get_user(_id: str, bot: Bot):
    "获取用户"
    user = await User.get(_id)
    if not user:
        user = User(id=_id)
        await user.insert()
    if user.bind_power == 0:
        user.bind_power = random() * 2
        await user.save()
    return user


def require(cost_coins: int = 0, only_check: bool = False, superuser: bool = False, vip: bool = False) -> User:
    "用于获取发送用户的权限函数，可指定最小权限等级以及消耗积分数量"

    async def _require(event: MessageEvent, matcher: Matcher, bot: Bot):
        user = await get_user(event.get_user_id(), bot)

        if superuser and not user.id in config.supermgr_ids:
            await matcher.finish("\n您没有权限使用此功能！", at_sender=True)

        if vip:
            session_id = get_session_id(event)
            vip_info = await get_vip(session_id)
            if not vip_info[0]:
                await matcher.finish("\n该功能需要对话开通 AI VIP！", at_sender=True)

        if cost_coins:
            if user.coins < cost_coins:
                await matcher.finish(
                    f"\n您的积分不足，至少需要{cost_coins}。", at_sender=True
                )
            if not only_check:
                await user.inc({User.coins: -cost_coins})
                await matcher.send(
                    f"\n您已被扣除所需的{cost_coins}点积分！", at_sender=True
                )
                await asyncio.sleep(1)
        return user

    return Depends(_require, validate=True)



def reply(required: bool = False) -> Reply | None:
    "获取单条回复信息"

    async def _reply(matcher: Matcher, event: MessageEvent):
        if required and not event.reply:
            await matcher.finish("\n必须回复一条消息才能使用此功能", at_sender=True)
        return event.reply

    return Depends(_reply, validate=True)


async def _get_flow_replies(
    replied: Annotated[Reply | None, reply()], bot: Bot
) -> list[Reply] | None:
    "获取回复链"
    if not replied:
        return None
    replies = [replied]
    while replies[-1].message["reply"]:
        replies.append(
            Reply.model_validate(
                await bot.get_msg(message_id=replies[-1].message["reply", 0].data["id"])
            )
        )
    return list(reversed(replies))


get_flow_replies = Depends(_get_flow_replies, validate=True)


def boolize(i: str | None) -> bool:
    return i.strip()[0].lower() in ("t", "y", "是", "真", "启") if i else False


def get_session_id(event: MessageEvent) -> str:
    "获取会话ID"
    if isinstance(event, GroupMessageEvent):
        return f"g{event.group_id}"
    return f"u{event.user_id}"


session_id_depends = Depends(get_session_id, validate=True)


async def get_nick(session_id: str, user_id: str, bot: Bot) -> str:
    "获取昵称"
    if session_id.startswith("g"):
        group_id = int(session_id[1:])
        member_info = await bot.get_group_member_info(
            group_id=group_id, user_id=int(user_id)
        )
        if member_info:
            return member_info["card"] or member_info["nickname"]

    user_info = await bot.get_stranger_info(user_id=int(user_id))
    return user_info["nickname"]


def nick_getter() -> Callable[[str], Awaitable[str]]:
    async def _nick_getter(
        session_id: Annotated[str, session_id_depends],
        bot: Bot,
    ) -> Callable[[str], Awaitable[str]]:
        async def _get_nick(user_id: str) -> str:
            return await get_nick(session_id, user_id, bot)

        return _get_nick

    return Depends(_nick_getter, validate=True)
