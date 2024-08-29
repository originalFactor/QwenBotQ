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

from datetime import timedelta, datetime
from http import HTTPStatus
from random import randint, choice
from typing import Annotated, Tuple
from socket import socket, AF_INET, SOCK_DGRAM
from nonebot import on_command, on_message
from nonebot.rule import to_me
from nonebot.params import EventPlainText
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent
import dashscope
from .database import (
    Couple,
    use_couple,
    find_couple,
    remove_couple,
    get_top10_users,
    UserWithNick,
    update_user,
    get_user
)
from .utils import still_valid
from .bot_utils import (
    arg_plain_text,
    require,
    arg,
    mentioned,
    u2uwn,
    GetMsgResult,
    reply
)
from . import config

# 设置dashscope sdk
dashscope.api_key = config.dashscope_api_key


LLMMatcher = on_message(to_me(), priority=20)

# 预连接UDP
if config.note_send_address:
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.connect((config.note_send_address, config.note_send_port))


@LLMMatcher.handle()
async def llm(
        user: Annotated[UserWithNick, require(0, config.llm_cost)],
        prompt: Annotated[str, EventPlainText()]
):
    "大模型回复"
    if prompt:
        if config.note_send_address:  # 彩蛋功能
            sock.send(prompt.encode())
        response = dashscope.Generation.call(
            model=config.model,
            messages=[
                {'role': 'system', 'content': user.system_prompt},  # type: ignore
                {'role': 'user', 'content': prompt}
            ],
            seed=randint(1, 10000),
            temprature=0.8,
            top_p=0.8,
            top_k=50,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK:  # type: ignore
            await LLMMatcher.finish(
                '\n大模型回答：\n' +
                response.output.choices[0].message.content,  # type: ignore
                at_sender=True
            )
        await LLMMatcher.finish(
            f"\n错误：API服务器返回状态码{response.status_code}！",  # type: ignore
            at_sender=True
        )
    await LLMMatcher.finish(
        "\n虽然你啥也没说，但是我记住你了！",
        at_sender=True
    )


PromptMatcher = on_command('设置系统提示词')


@PromptMatcher.handle()
async def set_prompt(
    user: Annotated[UserWithNick, require(0, config.set_prompt_cost)],
    prompt: Annotated[str, arg_plain_text]
):
    '设置系统提示词'
    user.system_prompt = prompt
    await update_user(user)
    await PromptMatcher.finish(
        '\n已尝试更新您的专属系统提示词',
        at_sender=True
    )

GetInformationMatcher = on_command('用户信息')


@GetInformationMatcher.handle()
async def get_information(
    user: Annotated[UserWithNick, require()],
    mention: Annotated[Tuple[UserWithNick, ...], mentioned()],
    bot: Bot
):
    '用户信息'
    user = mention[0] if mention else user
    if couple := await user.couple:
        cp_user = await u2uwn(await get_user(
            (await couple.opposite(user.id))
        ), bot)
    await GetInformationMatcher.finish(
        f'\n{user.id}的用户信息：\n'
        f'昵称：{user.nick}\n'
        f'积分：{user.coins}\n\t' +
        (
            f"已签到\n\t失效时间：{(await user.sign_expire).strftime('%Y/%m/%d %H:%M:%S')}\n"
            if await still_valid(user.last_signed_date) else
            "未签到\n"
        ) +
        f'权限等级：{user.permission}\n'
        f'系统提示词：{user.system_prompt}\n'
        '头像：' +
        MessageSegment.image(await user.avatar) +
        '本日老公：' +
        (
            f'{cp_user.nick} ({cp_user.id})\n'
            f'\t失效时间：{(await couple.expire).strftime("%Y/%m/%d %H:%M:%S")}'
            if couple else
            '未绑定'
        ),
        at_sender=True
    )

GrantMatcher = on_command('授予权限')


@GrantMatcher.handle()
async def grant_permission(
    user: Annotated[UserWithNick, require(2, config.grant_cost)],
    mention: Annotated[Tuple[UserWithNick, ...], mentioned(1)]
):
    '授予权限'
    mention[0].permission = max(user.permission-1, mention[0].permission)
    await update_user(mention[0])
    await GrantMatcher.finish(
        f"\n已授予{mention[0].permission}级权限给\n" +
        f'{mention[0].nick} ({mention[0].id})',
        at_sender=True
    )

BindMatcher = on_command('捆在一起')


@BindMatcher.handle()
async def bind(
    mention: Annotated[Tuple[UserWithNick, ...], mentioned(2)],
    _: Annotated[UserWithNick, require(1, config.bind_cost)]
):
    '绑定关系'
    cp = Couple(A=mention[0].id, B=mention[1].id, date=datetime.now())
    await use_couple(cp)
    await BindMatcher.finish(
        '\n已尝试绑定\n'
        f'{mention[0].nick} ({mention[0].id})\n'
        '和\n'
        f'{mention[1].nick} ({mention[1].id})\n'
        '为本日CP！\n'
        f'有效期至：{(await cp.expire).strftime("%Y/%m/%d %H:%M:%S")}',
        at_sender=True
    )


WifeMatcher = on_command('今日老公')


@WifeMatcher.handle()
async def wife(
    user: Annotated[UserWithNick, require()],
    event: GroupMessageEvent,
    bot: Bot
):
    '群友老公'
    if couple := await user.couple:
        cp_user = await u2uwn(await get_user(await couple.opposite(user.id)), bot)
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        cp_user = await u2uwn(await get_user(x['user_id']), bot)
        couple = Couple(A=user.id, B=cp_user.id, date=datetime.now())
        await use_couple(couple)
    await WifeMatcher.finish(
        '\n你今天的老公是：' +
        MessageSegment.image(await cp_user.avatar) +
        f'{cp_user.nick} ({cp_user.id})\n'
        f'过期时间：{(couple.date+timedelta(1)).strftime("%Y/%m/%d %H:%M:%S")}\n'
        '\n今日关系已绑定，要好好珍惜哦！',
        at_sender=True
    )

MembersMatcher = on_command('群友列表')


@MembersMatcher.handle()
async def group_members(event: GroupMessageEvent, bot: Bot):
    '群友列表'
    await MembersMatcher.finish(
        '\n' +
        (
            '\n'.join(
                [
                    f"{x['nickname']} ({x['user_id']})"
                    for x in (
                        await bot.get_group_member_list(
                            group_id=event.group_id
                        )
                    )
                ]
            )
        ),
        at_sender=True
    )

SignMatcher = on_command('签到')


@SignMatcher.handle()
async def sign(user: Annotated[UserWithNick, require()]):
    '每日签到'
    if not await still_valid(user.last_signed_date):
        coins = randint(config.daily_sign_min_coins,
                        config.daily_sign_max_coins)
        user.coins += coins
        user.last_signed_date = datetime.now()
        await update_user(user)
        await SignMatcher.finish(
            f'\n签到成功！本次获得{coins}个积分',
            at_sender=True
        )
    await SignMatcher.finish(
        "\n本日已签到！请勿重复签到！\n"
        '最近一次签到的过期时间：\n' +
        (await user.sign_expire).strftime("%Y/%m/%d %H:%M:%S"),
        at_sender=True
    )

RankMatcher = on_command('封神榜')


@RankMatcher.handle()
async def rank(bot: Bot):
    '积分排行榜'
    users = [await u2uwn(_, bot) for _ in await get_top10_users()]
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


RefreshMatcher = on_command('我不要和他玩')


@RefreshMatcher.handle()
async def refresh(
    user: Annotated[UserWithNick, require(0, config.refresh_price)],
    bot: Bot
):
    '解除绑定'
    if couple := await find_couple(user.id, True):
        await remove_couple(couple)
        cp_user = await u2uwn(await get_user(await couple.opposite(user.id)), bot)
    await RefreshMatcher.finish(
        '\n已解除和\n'
        f'{f"{cp_user.nick} ({cp_user.id})" if cp_user else "未绑定或已过期"}\n'
        '的绑定！',
        at_sender=True
    )

ChargeMatcher = on_command('印钞机')


@ChargeMatcher.handle()
async def charge(
    user: Annotated[UserWithNick, require(config.charge_min_perm)],
    argument: Annotated[Tuple[int], arg(int, 1)]
):
    '充值积分'
    user.coins += argument[0]
    await update_user(user)
    await ChargeMatcher.finish(
        f'\n已为您的账户充值{argument[0]}积分！',
        at_sender=True
    )

TransferMatcher = on_command('转账给')


@TransferMatcher.handle()
async def transfer(
    user: Annotated[UserWithNick, require()],
    mentions: Annotated[Tuple[UserWithNick, ...], mentioned(1)],
    argument: Annotated[Tuple[int], arg(int, 1)]
):
    '转账积分'
    if user.coins >= argument[0]:
        mentions[0].coins += argument[0]
        user.coins -= argument[0]
        await update_user(mentions[0])
        await update_user(user)
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

# [SYNC] `/fork`
ForkMatcher = on_command('我要这个')


@ForkMatcher.handle()
async def fork(
    replied: Annotated[GetMsgResult, reply(True)],
    bot: Bot,
    _: Annotated[UserWithNick, require(0, config.fork_cost)]
):
    '应用老搭'
    if replied.sender.user_id not in config.trusted_wife_source:
        await ForkMatcher.finish(
            '\n请使用可信的数据源！',
            at_sender=True
        )
    user = await u2uwn(await get_user(replied.message['at', 0].data['qq']), bot)
    user_wife = await u2uwn(await get_user(
        replied.message.extract_plain_text().split('(')[1].split(')')[0]
    ), bot)
    await use_couple(Couple(A=user.id, B=user_wife.id, date=datetime.now()))
    await ForkMatcher.finish(
        '\n已成功绑定\n'
        f'{user.nick} ({user.id})\n'
        '和\n'
        f'{user_wife.nick} ({user_wife.id})\n'
        '的关系！(来自可信来源的外部数据)',
        at_sender=True
    )

RenewMatcher = on_command('还要这个')


@RenewMatcher.handle()
async def renew(
    user: Annotated[UserWithNick, require(0, config.renew_cost)],
    bot: Bot
):
    '续期关系'
    if cp := await user.couple:
        cp.date += timedelta(1)
        await use_couple(cp)
        couple = await u2uwn(await get_user(await cp.opposite(user.id)), bot)
    await RenewMatcher.finish(
        '\n已成功续期您和\n'
        f'{f"{couple.nick} ({couple.id})" if couple else "未绑定或已过期"}\n'
        '的关系至\n'
        f'{(await cp.expire).strftime("%Y/%m/%d %H:%M:%S") if cp else "无数据"}',
        at_sender=True
    )
