# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"抽奖模块"

import re
from random import randint
from datetime import date, datetime, timedelta, time
from typing import Annotated

from arclet.alconna import Alconna, Args
from nonebot_plugin_alconna import on_alconna, Match
from nonebot import get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler

from . import config, driver
from .database import User, LotteryTicket
from .bot_utils import require


def get_nextday():
    return datetime.combine(date.today() + timedelta(1), time(12)).strftime(
        "%Y/%m/%d %H:%M:%S"
    )


# 购买奖号命令
buy_cmd = Alconna("购买奖号", Args["number?", str])
BuyMatcher = on_alconna(buy_cmd, block=True)


@BuyMatcher.handle()
async def buy_ticket(
    user: Annotated[User, require(config.lottery.ticket_price, True)],
    number: Match[str],
    event: GroupMessageEvent,
):
    "购买抽奖号码"

    group_id = str(event.group_id)
    if group_id not in config.lottery.groups:
        await BuyMatcher.finish("\n本群未开启抽奖功能。", at_sender=True)

    if not number.available:
        await BuyMatcher.finish(
            f"\n用法：购买奖号 <6位数字>\n" f"花费 {config.lottery.ticket_price} 积分",
            at_sender=True,
        )

    num = number.result.strip()
    if not re.fullmatch(r"\d{6}", num):
        await BuyMatcher.finish("\n奖号必须是6位数字。", at_sender=True)

    # 检查今日是否已购买
    existing = await LotteryTicket.find_one(
        LotteryTicket.user_id == user.id,
    )
    if existing:
        await BuyMatcher.finish(
            f"\n您已经购买过奖号，开奖后可再次购买。",
            at_sender=True,
        )

    # 检查奖号全局唯一（同一期）
    duplicate = await LotteryTicket.find_one(
        LotteryTicket.number == num,
    )
    if duplicate:
        await BuyMatcher.finish("\n该奖号已被其他人选择，请换一个。", at_sender=True)

    ticket = LotteryTicket(user_id=user.id, number=num)
    await ticket.insert()

    await user.inc({User.coins: -config.lottery.ticket_price})

    await BuyMatcher.finish(
        "购买成功！" f"\n奖号：{num}" f"\n开奖时间：{get_nextday()}",
        at_sender=True,
    )


# 查看我的奖号
MyTicketMatcher = on_alconna(Alconna("我的奖号"), block=True)


@MyTicketMatcher.handle()
async def my_ticket(
    user: Annotated[User, require()],
):
    "查看当期奖号"

    # 也查今天开奖的（还没开的话）
    ticket = await LotteryTicket.find_one(
        LotteryTicket.user_id == user.id,
    )

    if not ticket:
        await MyTicketMatcher.finish("\n您当前没有待开奖的奖号。", at_sender=True)

    await MyTicketMatcher.finish(
        f"\n您的奖号：{ticket.number}\n" f"开奖日期：{get_nextday()}",
        at_sender=True,
    )


def match_digits(ticket_num: str, winning_num: str) -> int:
    "计算匹配位数"
    return sum(a == b for a, b in zip(ticket_num, winning_num))


async def draw_lottery():
    "每日开奖"

    # 生成6位随机数
    winning = f"{randint(0, 999999):06d}"
    logger.info(f"今日开奖号码：{winning}")

    # 查找今天开奖的所有票
    tickets = await LotteryTicket.all().to_list()

    if not tickets:
        logger.info("今日无人参与抽奖")
        # 仍然在群里公布开奖号码
        bot = get_bot()
        for group_id in config.lottery.groups:
            await bot.send_msg(
                group_id=int(group_id),
                message=f"【每日抽奖开奖】\n开奖号码：{winning}\n今日无人参与抽奖",
            )
        return

    # 计算中奖
    winners: list[tuple[str, str, int, int]] = []  # (user_id, number, matches, reward)
    for ticket in tickets:
        matches = match_digits(ticket.number, winning)
        if matches > 0:
            reward = matches * config.lottery.reward_per_match
            # 发放奖励
            user = await User.get(ticket.user_id)
            if user:
                await user.inc({User.coins: reward})
            winners.append((ticket.user_id, ticket.number, matches, reward))

    # 构建消息，每个群只展示本群成员的中奖信息
    bot = get_bot()
    for group_id in config.lottery.groups:
        # 获取本群成员列表
        try:
            members = await bot.get_group_member_list(group_id=int(group_id))  # type: ignore
            member_ids = {str(m["user_id"]): m["nickname"] for m in members}
        except Exception:
            member_ids = {}

        group_winners = [(*w, member_ids[w[0]]) for w in winners if w[0] in member_ids]

        msg = f"【每日抽奖开奖】\n开奖号码：{winning}\n本期参与人数：{len(tickets)}"
        if group_winners:
            msg += "\n🎉 中奖名单："
            for user_id, number, matches, reward, user_nick in group_winners:
                msg += (
                    f"\n- {user_nick}({user_id})"
                    f"\n  奖号 {number}"
                    f"\n  匹配 {matches} 位"
                    f"\n  获得 {reward} 积分"
                )
        else:
            msg += "\n本群无人中奖"
        await bot.send_msg(group_id=int(group_id), message=msg)

    # 清理已开奖的票据
    await LotteryTicket.delete_all()
    logger.info(f"抽奖开奖完成，共 {len(winners)} 人中奖")


ForceDrawMatcher = on_alconna(Alconna("提前开奖"), block=True)


@ForceDrawMatcher.handle()
async def force_draw_lottery(
    user: Annotated[User, require(superuser=True)],
):
    "强制开奖"
    await draw_lottery()
    await ForceDrawMatcher.finish("\n已提前开奖", at_sender=True)


@driver.on_startup
async def register_lottery_scheduler():
    "注册抽奖定时任务"
    scheduler.add_job(
        draw_lottery,
        "cron",
        hour=12,
        minute=0,
        id="daily_lottery_draw",
        replace_existing=True,
    )
    logger.info("已注册每日抽奖定时任务（每天中午12:00）")
