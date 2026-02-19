# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"绑定相关"

from random import choice, random
from datetime import date, timedelta
from typing import Annotated

from nonebot_plugin_alconna import on_alconna, Match, At
from arclet.alconna import Alconna, Args
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Bot,
    MessageSegment,
    MessageEvent,
)

from . import config
from .database import User, apply_bind, BindRequest
from .bot_utils import require, get_user, get_nick, get_session_id, send_session


WifeMatcher = on_alconna(Alconna("今日老公"), block=True)


@WifeMatcher.handle()
async def wife(user: Annotated[User, require()], event: GroupMessageEvent, bot: Bot):
    "群友老公"
    if user.binded and user.binded.expire > date.today():
        cp_user = await get_user(user.binded.id)
        expire = user.binded.expire
    else:
        members = await bot.get_group_member_list(group_id=event.group_id)
        while True:
            x = choice(members)
            cp_user = await get_user(str(x["user_id"]))
            power = random() * 2
            if (
                (cp_user.id == user.id)
                or (cp_user.binded and cp_user.binded.expire > date.today())
                or (cp_user.bind_power > power)
            ):
                members.remove(x)
                power += 0.2
                continue
            break
        expire = await apply_bind(user, cp_user)
    cp_nick = await get_nick(get_session_id(event), cp_user.id, bot)
    await WifeMatcher.finish(
        "\n你今天的老公是："
        + MessageSegment.image(f"https://q1.qlogo.cn/g?b=qq&nk={cp_user.id}&s=5")
        + f"{cp_nick} ({cp_user.id})\n"
        f'过期时间：{expire.strftime("%Y/%m/%d")}\n'
        "\n今日关系已绑定，要好好珍惜哦！",
        at_sender=True,
    )


RefreshMatcher = on_alconna(Alconna("换老公"), block=True)


@RefreshMatcher.handle()
async def refresh(user: Annotated[User, require(config.price.refresh_price)]):
    "解除绑定"
    await user.set({"binded": None})

    await RefreshMatcher.finish("\n已解除绑定！", at_sender=True)


RenewMatcher = on_alconna(Alconna("续期", Args["days?", int]), block=True)


@RenewMatcher.handle()
async def renew(
    user: Annotated[User, require()], bot: Bot, event: MessageEvent, days: Match[int]
):
    "续期关系"
    if user.binded and user.binded.expire > date.today():
        days_i = days.result if days.available else 1

        if days_i < 1:
            await RenewMatcher.finish("\n续期天数不能小于1天", at_sender=True)

        if user.coins < config.price.renew_cost * days_i:
            await RenewMatcher.finish("\n您的余额不足", at_sender=True)

        w = await get_user(user.binded.id)
        new_exp = user.binded.expire + timedelta(days=days_i)

        await w.set({"binded.expire": new_exp})
        await user.set({"binded.expire": new_exp})

        elapsed_coins = config.price.renew_cost * days_i
        await user.inc({"coins": -elapsed_coins})

        w_nick = await get_nick(get_session_id(event), w.id, bot)
        await RenewMatcher.finish(
            "\n已成功续期您和\n"
            f"{w_nick} ({w.id})\n"
            "的关系至\n"
            f'{user.binded.expire.strftime("%Y/%m/%d")}\n'
            f"消耗 {elapsed_coins} 积分",
            at_sender=True,
        )

    await RenewMatcher.finish("\n无绑定数据", at_sender=True)


RequestMatcher = on_alconna(
    Alconna("申请绑定", Args["to?", At]), block=True, use_origin=True
)


@RequestMatcher.handle()
async def request(
    user: Annotated[User, require()],
    bot: Bot,
    event: GroupMessageEvent,
    to: Match[At],
):
    "申请绑定"

    if not to.available:
        await RequestMatcher.finish("\n用法：申请绑定 @用户", at_sender=True)

    if user.binded and user.binded.expire > date.today():
        if user.binded.id == to.result.target:
            await RequestMatcher.finish("\n您已绑定该用户，无需申请", at_sender=True)
        await RequestMatcher.finish("\n您已绑定其他用户，请先解绑", at_sender=True)

    binded = False
    async for req in BindRequest.find({"to_id": user.id}):
        user_nick = await get_nick(req.requested_session, user.id, bot)
        if req.from_id == to.result.target:
            binded = True
            cp = await get_user(req.from_id)
            expire = await apply_bind(cp, user)
            cp_nick = await get_nick(get_session_id(event), cp.id, bot)
            await RequestMatcher.send(
                f"\n您和 {cp_nick} ({cp.id}) 已绑定\n"
                f"过期时间：{expire.strftime('%Y/%m/%d')}",
                at_sender=True,
            )
            await send_session(
                bot,
                req.requested_session,
                (
                    MessageSegment.at(cp.id)
                    + f"\n{user_nick} ({user.id}) 已接受您的绑定请求\n"
                    f"过期时间：{expire.strftime('%Y/%m/%d')}"
                ),
            )
        else:
            await send_session(
                bot,
                req.requested_session,
                (
                    MessageSegment.at(cp.id)
                    + f"\n{user_nick} ({user.id}) 已拒绝您的绑定请求"
                ),
            )
    await BindRequest.find({"to_id": user.id}).delete()

    if binded:
        await RequestMatcher.finish()

    cp_user = await get_user(to.result.target)
    cp_nick = await get_nick(get_session_id(event), cp_user.id, bot)

    if cp_user.binded and cp_user.binded.expire > date.today():
        await RequestMatcher.finish(
            f"\n{cp_nick} ({cp_user.id}) 已绑定其他用户", at_sender=True
        )

    await BindRequest.find_one({"from_id": user.id}).delete()
    await BindRequest(
        from_id=user.id,
        to_id=cp_user.id,
        requested_session=get_session_id(event),
    ).insert()

    await RequestMatcher.finish(
        f"\n您已成功申请绑定 {cp_nick} ({cp_user.id})", at_sender=True
    )
