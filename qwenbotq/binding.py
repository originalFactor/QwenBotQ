# Copyright (C) 2024 Administrator
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

'绑定相关'

from random import choice
from datetime import date, timedelta
from typing import Annotated, Sequence
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageSegment
from nonebot.adapters.onebot.v11.event import Reply
from . import config
from .database import User, apply_bind
from .bot_utils import (
    mentioned,
    require,
    reply,
    get_user
)


BindMatcher = on_command('官宣', block=True)

@BindMatcher.handle()
async def bind(
    mention: Annotated[Sequence[User], mentioned(2)],
    _: Annotated[User, require(1, config.bind_cost)]
):
    '绑定关系'
    expire = await apply_bind(mention[0], mention[1])
    await BindMatcher.finish(
        '\n已尝试绑定\n'
        f'{mention[0].nick} ({mention[0].id})\n'
        '和\n'
        f'{mention[1].nick} ({mention[1].id})\n'
        '为本日CP！\n'
        f'有效期至：{expire.strftime("%Y/%m/%d")}',
        at_sender=True
    )


WifeMatcher = on_command('今日老公', block=True)

@WifeMatcher.handle()
async def wife(
    user: Annotated[User, require()],
    event: GroupMessageEvent,
    bot: Bot
):
    '群友老公'
    if user.binded and user.binded.expire > date.today():
        cp_user = await get_user(user.binded.id, None, bot)
        expire = user.binded.expire
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        cp_user = await get_user(x['user_id'], x['nickname'], bot)
        expire = await apply_bind(user, cp_user)
    await WifeMatcher.finish(
        '\n你今天的老公是：' +
        MessageSegment.image(f'https://q1.qlogo.cn/g?b=qq&nk={cp_user.id}&s=5') +
        f'{cp_user.nick} ({cp_user.id})\n'
        f'过期时间：{expire.strftime("%Y/%m/%d")}\n'
        '\n今日关系已绑定，要好好珍惜哦！',
        at_sender=True
    )


RefreshMatcher = on_command('换老公', block=True)

@RefreshMatcher.handle()
async def refresh(
    user: Annotated[User, require(0, config.refresh_price)]
):
    '解除绑定'
    await user.set({User.binded: None})

    await RefreshMatcher.finish(
        '\n已解除绑定！',
        at_sender=True
    )


ForkMatcher = on_command('恢复记录', block=True)

@ForkMatcher.handle()
async def fork(
    bot: Bot,
    _: Annotated[User, require(0, config.fork_cost)],
    replied: Annotated[Reply, reply(True)]):
    '应用老搭'
    if replied.sender.user_id not in config.trusted_wife_source:
        await ForkMatcher.finish(
            '\n请使用可信的数据源！',
            at_sender=True
        )
    first = replied.message['at', 0].data
    user = await get_user(first['qq'], first['name'], bot)
    plain = replied.message.extract_plain_text()
    nick = plain.split(':',1)[1].split('(',1)[0]
    _id = plain.split('(',1)[1].split(')',1)[0]
    user_wife = await get_user(_id, nick, bot)
    expire = await apply_bind(user, user_wife)
    await ForkMatcher.finish(
        '\n已成功绑定\n'
        f'{user.nick} ({user.id})\n'
        '和\n'
        f'{user_wife.nick} ({user_wife.id})\n'
        '的关系！(来自可信来源的外部数据)\n'
        f'过期时间：{expire.strftime("%Y/%m/%d")}',
        at_sender=True
    )

RenewMatcher = on_command('续期', block=True)


@RenewMatcher.handle()
async def renew(
    user: Annotated[User, require(0, config.renew_cost)],
    bot: Bot
):
    '续期关系'
    if user.binded:
        w = await get_user(user.binded.id, None, bot)
        await w.inc({User.binded.expire: timedelta(1)})
        await user.inc({User.binded.expire: timedelta(1)})
        await RenewMatcher.finish(
            '\n已成功续期您和\n'
            f"{user.nick} ({user.id})\n"
            '的关系至\n'
            f'{user.binded.expire.strftime("%Y/%m/%d %H:%M:%S")}',
            at_sender=True
        )
    await RenewMatcher.finish(
        '\n无绑定数据',
        at_sender=True
    )
