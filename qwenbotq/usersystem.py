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

"Core module of QwenBotQ"

from datetime import timedelta, date
from random import randint
from typing import Annotated, Sequence
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from beanie.odm.operators.update.general import Max

from . import config
from .bot_utils import (
    require,
    arg,
    mentioned,
    get_user
)
from .database import User


GetInformationMatcher = on_command('用户信息', block=True)

@GetInformationMatcher.handle()
async def get_information(
    user: Annotated[User, require()],
    mention: Annotated[Sequence[User], mentioned()],
    bot: Bot
):
    '用户信息'
    user = mention[0] if mention else user
    cp = await get_user(user.binded.id, None, bot) if user.binded else None
    await GetInformationMatcher.finish(
        f'\n{user.id}的用户信息：\n'
        f'昵称：{user.nick}\n'
        f'积分：{user.coins}\n\t' +
        (
            f"已签到\n\t失效日期：{user.sign_expire.strftime('%Y/%m/%d')}\n"
            if user.sign_expire>date.today() else
            "未签到\n"
        ) +
        f'权限等级：{user.permission}\n'
        f'使用模型：{user.model}\n'
        f'\t系统提示词：{user.system_prompt}\n'
        '头像：' +
        MessageSegment.image(f'https://q1.qlogo.cn/g?b=qq&nk={user.id}&s=5') +
        '本日老公：' +
        (
            f'{cp.nick} ({cp.id})\n'
            f'\t失效日期：{user.binded.expire.strftime("%Y/%m/%d")}'
            if user.binded else
            '未绑定'
        ),
        at_sender=True
    )


GrantMatcher = on_command('授予权限', block=True)

@GrantMatcher.handle()
async def grant_permission(
    user: Annotated[User, require(2, config.grant_cost)],
    mention: Annotated[Sequence[User], mentioned(1)]
):
    '授予权限'
    await mention[0].update(Max({User.permission: user.permission-1}))
    await GrantMatcher.finish(
        f"\n已授予{mention[0].permission}级权限给\n" +
        f'{mention[0].nick} ({mention[0].id})',
        at_sender=True
    )


SignMatcher = on_command('签到', block=True)

@SignMatcher.handle()
async def sign(user: Annotated[User, require()]):
    '每日签到'
    if user.sign_expire <= date.today():
        coins = randint(
            config.daily_sign_min_coins,
            config.daily_sign_max_coins
        )
        await user.set({
            User.sign_expire: date.today()+timedelta(1)
        })
        await user.inc({User.coins: coins})
        await SignMatcher.finish(
            f'\n签到成功！本次获得{coins}个积分\n'
            f'过期时间：{user.sign_expire.strftime("%Y/%m/%d")}',
            at_sender=True
        )
    await SignMatcher.finish(
        "\n本日已签到！请勿重复签到！\n"
        '最近一次签到的过期时间：\n' +
        user.sign_expire.strftime("%Y/%m/%d"),
        at_sender=True
    )


RankMatcher = on_command('积分榜', block=True)

@RankMatcher.handle()
async def rank():
    '积分排行榜'
    users = [_ async for _ in User.find().sort(('coins', -1)).limit(10)]
    await RankMatcher.finish(
        '\n积分排行榜：\n' +
        (
            '\n'.join(
                [
                    f'[{x+1}] {users[x].nick} ({users[x].id}) : {users[x].coins}'
                    for x in range(len(users))
                ]
            )
        ),
        at_sender=True
    )


ChargeMatcher = on_command('印钞机', block=True)

@ChargeMatcher.handle()
async def charge(
    user: Annotated[User, require(config.charge_min_perm)],
    argument: Annotated[Sequence[int], arg(int, 1)]
):
    '充值积分'
    await user.inc({User.coins: argument[0]})
    await ChargeMatcher.finish(
        f'\n已为您的账户充值{argument[0]}积分！',
        at_sender=True
    )


TransferMatcher = on_command('转账给', block=True)

@TransferMatcher.handle()
async def transfer(
    user: Annotated[User, require()],
    mentions: Annotated[Sequence[User], mentioned(1)],
    argument: Annotated[Sequence[int], arg(int, 1)]
):
    '转账积分'
    if argument[0] < 0:
        await TransferMatcher.finish(
            '\n不允许反向转账积分！',
            at_sender=True
        )
    if user.id == mentions[0].id:
        await TransferMatcher.finish(
            '\n不允许给自己转账！',
            at_sender=True
        )
    if user.coins >= argument[0]:
        await mentions[0].inc({User.coins: argument[0]})
        await user.inc({User.coins: -argument[0]})
        await TransferMatcher.finish(
            '\n成功给\n'
            f'{mentions[0].nick} ({mentions[0].id})\n'
            f'转账了{argument[0]}积分！',
            at_sender=True
        )
    await TransferMatcher.finish(
        f'\n您的积分余额不足以转账{argument[0]}积分！',
        at_sender=True
    )
