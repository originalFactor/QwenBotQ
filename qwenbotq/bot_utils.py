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

from typing import Annotated, List, Optional, Sequence
from datetime import date

from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Reply
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, EventMessage
from nonebot.rule import Rule

from .database import User


async def get_user(_id: str, nick: Optional[str], bot: Bot):
    '获取用户'
    user = await User.get(_id)
    if not user:
        user = User(id=_id)
        await user.insert()
    if user.profile_expire <= date.today():
        await user.set({User.nick: (await bot.get_stranger_info(user_id=_id))['nickname']})
    if nick:
        user.nick = nick
    return user

def require(cost_permission: int = 0, cost_coins: int = 0, only_check: bool = False):
    "用于获取发送用户的权限函数，可指定最小权限等级以及消耗积分数量"
    @Depends
    async def _require(event: MessageEvent, matcher: Matcher, bot: Bot) -> User:
        user = await get_user(event.get_user_id(), event.sender.nickname, bot)
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
            if not only_check:
                await user.inc({User.coins: -cost_coins})
                await matcher.send(
                    f"\n您已被扣除所需的{cost_coins}点积分！",
                    at_sender=True
                )
        return user
    return _require


@Depends
async def arg_plain_text(args: Annotated[Message, CommandArg()]) -> str:
    '获取命令纯文本参数'
    return args.extract_plain_text().strip()


def arg(tp: type, least: int = 0):
    "获取至少least个tp类型的命令参数"
    @Depends
    async def _arg(
            matcher: Matcher,
            args: Annotated[str, arg_plain_text]
    ) -> List[tp]: # type: ignore
        try:
            if len(x := list(map(tp, args.strip().split()))) >= least:
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
        msg: Annotated[Message, EventMessage()],
        args: Annotated[Sequence[str], arg(str)]
    ) -> List[User]:
        mentioned_users = (
            [await get_user(_.data['qq'], _.data['name'], bot) for _ in msg['at']]+
            [await get_user(_[1:], None, bot) for _ in args if _.startswith('@')]
        )
        if len(mentioned_users) >= least:
            return mentioned_users
        await matcher.finish(
            f'\n该功能至少要提及{least}个用户。',
            at_sender=True
        )
    return _mentioned


def reply(required: bool = False):
    "获取单条回复信息"
    @Depends
    async def _reply(
            matcher: Matcher,
            event: MessageEvent) -> Optional[Reply]:
        if required and not event.reply:
            await matcher.finish(
                "\n必须回复一条消息才能使用此功能",
                at_sender=True
            )
        return event.reply
    return _reply


@Rule
async def strict_to_me(event: MessageEvent) -> bool:
    '剔除掉回复的隐藏@后的提及我'
    if event.to_me and (event.message_type == 'private' or not event.reply):
        return True
    for segment in event.message['at']:
        if segment.data['qq'] == str(event.self_id):
            return True
    return False

@Depends
async def get_flow_replies(
    replied: Annotated[Optional[Reply], reply()],
    bot: Bot
    ) -> Optional[List[Reply]]:
    '获取回复链'
    if not replied:
        return None
    replies = [replied]
    while replies[-1].message['reply']:
        replies.append(
            Reply.model_validate(
                await bot.get_msg(
                    message_id=replies[-1].message['reply',0].data['id']
                )
            )
        )
    return reversed(replies)
