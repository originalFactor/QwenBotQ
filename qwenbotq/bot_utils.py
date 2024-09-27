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

from typing import Union, Annotated, List, Optional, Sequence

from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.adapters.onebot.v11.event import Reply
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from nonebot.rule import Rule

from .database import User


@Depends
async def event_original_message(event: MessageEvent) -> Message:
    '获取事件的原始消息（未去除@bot和回复）'
    return event.original_message

def require(cost_permission: int = 0, cost_coins: int = 0, only_check: bool = False):
    "用于获取发送用户的权限函数，可指定最小权限等级以及消耗积分数量"
    @Depends
    async def _require(event: MessageEvent, matcher: Matcher, bot: Bot) -> User:
        user = await User.get(event.user_id, bot)
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
                user.coins -= cost_coins
                await user.update()
                await matcher.send(
                    f"\n您已被扣除所需的{cost_coins}点积分！",
                    at_sender=True
                )
        if event.sender.nickname:
            user.nick = event.sender.nickname
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
    ) -> List[tp]:
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
        msg: Annotated[Message, event_original_message],
        args: Annotated[Sequence[str], arg(str)]
    ) -> List[User]:
        mentioned_users = (
            [await User.get(_.data['qq'], bot) for _ in msg['at']]+
            [await User.get(_[1:], bot) for _ in args if _.startswith('@')]
        )
        if len(mentioned_users) >= least:
            return mentioned_users
        await matcher.finish(
            f'\n该功能至少要提及{least}个用户。',
            at_sender=True
        )
    return _mentioned


def reply(required: bool = False):
    "The dependency for replied message"
    @Depends
    async def _reply(
            matcher: Matcher,
            event: MessageEvent) -> Union[Reply, None]:
        if required and not event.reply:
            await matcher.finish(
                "\n必须回复一条消息才能使用此功能",
                at_sender=True
            )
        return event.reply
    return _reply


@Rule
def strict_to_me(event: MessageEvent) -> bool:
    if event.original_message['at']:
        if (
            event.original_message['at', 0].data['qq'] == str(event.self_id)
            or
            event.message_type == 'private'
        ):
            return True
    return False

async def get_replies(reply: Reply, bot: Bot) -> List[Reply]:
    if reply.message['reply']:
        return (
            await get_replies(
                Reply.model_validate(
                    await bot.get_msg(
                        message_id=reply.message['reply',0].data['id']
                    )
                ),
                bot
            )
            +
            [reply]
        )
    return [reply]

@Depends
async def get_flow_replies(replied: Annotated[Optional[Reply], reply()], bot: Bot) -> Optional[List[Reply]]:
    return await get_replies(replied, bot) if replied else None