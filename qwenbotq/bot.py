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
from random import randint, choice
from typing import Annotated, Optional, Sequence
from urllib.error import HTTPError
from math import ceil

from nonebot import on_message, on_command
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot.adapters.onebot.v11.event import Reply, GroupMessageEvent
from nonebot.params import EventPlainText
from openai import AsyncOpenAI

from . import config
from .bot_utils import (
    arg_plain_text,
    require,
    arg,
    mentioned,
    reply,
    strict_to_me,
    get_flow_replies
)
from .database import Couple, User, get_top10_users
from .utils import sum_tokens

# 初始化异步OpenAI客户端对象
openai = AsyncOpenAI(
    api_key=config.api_key,
    base_url=config.base_url
)


LLMMatcher = on_message(strict_to_me, priority=20)


@LLMMatcher.handle()
async def llm(
        user: Annotated[User, require(0,1,True)],
        prompt: Annotated[str, EventPlainText()],
        replies: Annotated[Optional[Sequence[Reply]], get_flow_replies],
        bot: Bot
):
    "大模型回复"
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
            user.coins -= (usage := ceil(
                response.usage.prompt_tokens/1000*config.models[user.model][0]
                +
                response.usage.completion_tokens/1000*config.models[user.model][1]
            ))
            await user.update()
            await LLMMatcher.finish(
                '\n'+response.choices[0].message.content+'\n'
                f'-( 本次共消耗{usage}积分 )-',
                reply_message=True
            )
    await LLMMatcher.finish(
        "\n虽然你啥也没说，但是我记住你了！",
        at_sender=True
    )


PromptMatcher = on_command('设置系统提示词', block=True)


@PromptMatcher.handle()
async def set_prompt(
    user: Annotated[User, require(0, config.set_prompt_cost)],
    prompt: Annotated[str, arg_plain_text]
):
    '设置系统提示词'
    user.system_prompt = prompt
    await user.update()
    await PromptMatcher.finish(
        '\n已尝试更新您的专属系统提示词',
        at_sender=True
    )

GetInformationMatcher = on_command('用户信息', block=True)


@GetInformationMatcher.handle()
async def get_information(
    user: Annotated[User, require()],
    mention: Annotated[Sequence[User], mentioned()]
):
    '用户信息'
    user = mention[0] if mention else user
    cp = await user.couple
    await GetInformationMatcher.finish(
        f'\n{user.id}的用户信息：\n'
        f'昵称：{user.nick}\n'
        f'积分：{user.coins}\n\t' +
        (
            f"已签到\n\t失效时间：{user.sign_expire.strftime('%Y/%m/%d %H:%M:%S')}\n"
            if user.sign_expire>datetime.now() else
            "未签到\n"
        ) +
        f'权限等级：{user.permission}\n'
        f'使用模型：{user.model}\n'
        f'\t系统提示词：{user.system_prompt}\n'
        '头像：' +
        MessageSegment.image(user.avatar) +
        '本日老公：' +
        (
            f'{cp.user.nick} ({cp.user.id})\n'
            f'\t失效时间：{cp.expire.strftime("%Y/%m/%d %H:%M:%S")}'
            if cp else
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
    mention[0].permission = max(user.permission-1, mention[0].permission)
    await mention[0].update()
    await GrantMatcher.finish(
        f"\n已授予{mention[0].permission}级权限给\n" +
        f'{mention[0].nick} ({mention[0].id})',
        at_sender=True
    )

BindMatcher = on_command('官宣', block=True)


@BindMatcher.handle()
async def bind(
    mention: Annotated[Sequence[User], mentioned(2)],
    _: Annotated[User, require(1, config.bind_cost)]
):
    '绑定关系'
    cp = Couple(A=mention[0].id, B=mention[1].id, expire=datetime.today()+timedelta(1))
    await cp.apply()
    await BindMatcher.finish(
        '\n已尝试绑定\n'
        f'{mention[0].nick} ({mention[0].id})\n'
        '和\n'
        f'{mention[1].nick} ({mention[1].id})\n'
        '为本日CP！\n'
        f'有效期至：{cp.expire.strftime("%Y/%m/%d %H:%M:%S")}',
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
    if couple := await user.couple:
        cp_user = couple.user
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        cp_user = await User.get(x['user_id'], bot)
        cp_user.nick = x['nickname']
        couple = Couple(A=user.id, B=cp_user.id, expire=datetime.today()+timedelta(1))
        await couple.apply()
    await WifeMatcher.finish(
        '\n你今天的老公是：' +
        MessageSegment.image(cp_user.avatar) +
        f'{cp_user.nick} ({cp_user.id})\n'
        f'过期时间：{couple.expire.strftime("%Y/%m/%d %H:%M:%S")}\n'
        '\n今日关系已绑定，要好好珍惜哦！',
        at_sender=True
    )

MembersMatcher = on_command('群友列表', block=True)


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

SignMatcher = on_command('签到', block=True)


@SignMatcher.handle()
async def sign(user: Annotated[User, require()]):
    '每日签到'
    if user.sign_expire < datetime.now():
        coins = randint(config.daily_sign_min_coins,
                        config.daily_sign_max_coins)
        user.coins += coins
        user.sign_expire = datetime.today()+timedelta(1)
        await user.update()
        await SignMatcher.finish(
            f'\n签到成功！本次获得{coins}个积分\n'
            f'过期时间：{user.sign_expire.strftime("%Y/%m/%d %H:%M:%S")}',
            at_sender=True
        )
    await SignMatcher.finish(
        "\n本日已签到！请勿重复签到！\n"
        '最近一次签到的过期时间：\n' +
        user.sign_expire.strftime("%Y/%m/%d %H:%M:%S"),
        at_sender=True
    )

RankMatcher = on_command('积分榜', block=True)


@RankMatcher.handle()
async def rank():
    '积分排行榜'
    users = await get_top10_users()
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


RefreshMatcher = on_command('换老公', block=True)


@RefreshMatcher.handle()
async def refresh(
    user: Annotated[User, require(0, config.refresh_price)]
):
    '解除绑定'
    cpinfo = await user.couple
    if couple := await Couple.get(user.id):
        await couple.delete()

    await RefreshMatcher.finish(
        '\n已解除和\n'
        f'{f"{cpinfo.user.nick} ({cpinfo.user.id})" if cpinfo else "未绑定或已过期"}\n'
        '的绑定！',
        at_sender=True
    )

ChargeMatcher = on_command('印钞机', block=True)


@ChargeMatcher.handle()
async def charge(
    user: Annotated[User, require(config.charge_min_perm)],
    argument: Annotated[Sequence[int], arg(int, 1)]
):
    '充值积分'
    user.coins += argument[0]
    await user.update()
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
        mentions[0].coins += argument[0]
        user.coins -= argument[0]
        await mentions[0].update()
        await user.update()
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
    user = await User.get(replied.message['at', 0].data['qq'], bot)
    user_wife = await User.get(
        replied.message.extract_plain_text().split('(')[1].split(')')[0],
        bot
    )
    await Couple(A=user.id, B=user_wife.id, expire=datetime.today()+timedelta(1)).apply()
    await ForkMatcher.finish(
        '\n已成功绑定\n'
        f'{user.nick} ({user.id})\n'
        '和\n'
        f'{user_wife.nick} ({user_wife.id})\n'
        '的关系！(来自可信来源的外部数据)',
        at_sender=True
    )

RenewMatcher = on_command('续期', block=True)


@RenewMatcher.handle()
async def renew(
    user: Annotated[User, require(0, config.renew_cost)]
):
    '续期关系'
    if cp := await Couple.get(user.id):
        cp.expire += timedelta(1)
        await cp.update()
    couple = await user.couple
    await RenewMatcher.finish(
        '\n已成功续期您和\n'
        f'{f"{couple.user.nick} ({couple.user.id})" if couple else "未绑定或已过期"}\n'
        '的关系至\n'
        f'{couple.expire.strftime("%Y/%m/%d %H:%M:%S") if couple else "无数据"}',
        at_sender=True
    )


ModelChangeMatcher = on_command('更改模型', block=True)
@ModelChangeMatcher.handle()
async def model_change(
    user: Annotated[User, require()],
    args: Annotated[str, arg_plain_text]
):
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
    await user.update()
    await ModelChangeMatcher.finish(
        '\n成功为您更换模型。',
        at_sender=True
    )
