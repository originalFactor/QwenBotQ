# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"绑定相关"

from random import choice, random
from datetime import date, timedelta
from typing import Annotated

from nonebot_plugin_alconna import on_alconna
from arclet.alconna import Alconna
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Bot,
    MessageSegment,
    MessageEvent,
)

from . import config
from .database import User, apply_bind
from .bot_utils import require, get_user, get_nick, get_session_id


WifeMatcher = on_alconna(Alconna("今日老公"), block=True)


@WifeMatcher.handle()
async def wife(user: Annotated[User, require()], event: GroupMessageEvent, bot: Bot):
    "群友老公"
    if user.binded and user.binded.expire > date.today():
        cp_user = await get_user(user.binded.id, bot)
        expire = user.binded.expire
    else:
        members = await bot.get_group_member_list(group_id=event.group_id)
        while True:
            x = choice(members)
            cp_user = await get_user(str(x["user_id"]), bot)
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


RenewMatcher = on_alconna(Alconna("续期"), block=True)


@RenewMatcher.handle()
async def renew(
    user: Annotated[User, require(config.price.renew_cost)],
    bot: Bot,
    event: MessageEvent,
):
    "续期关系"
    if user.binded:
        w = await get_user(user.binded.id, bot)
        new_exp = user.binded.expire + timedelta(1)
        await w.set({"binded.expire": new_exp})
        await user.set({"binded.expire": new_exp})
        w_nick = await get_nick(get_session_id(event), w.id, bot)
        await RenewMatcher.finish(
            "\n已成功续期您和\n"
            f"{w_nick} ({w.id})\n"
            "的关系至\n"
            f'{user.binded.expire.strftime("%Y/%m/%d")}',
            at_sender=True,
        )
    await RenewMatcher.finish("\n无绑定数据", at_sender=True)
