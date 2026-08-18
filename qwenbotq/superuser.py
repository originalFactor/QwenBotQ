from typing import Annotated, cast
from re import search
from pytimeparse2 import parse
from nonebot_plugin_alconna import Alconna, Option, on_alconna, Args, Match, At, Query
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.adapters.onebot.v11.event import (
    GroupMessageEvent,
    GroupRequestEvent,
    MessageEvent,
)
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.matcher import Matcher
from nonebot import on_command, on_request
from nonebot.params import Depends
from .bot_utils import nick_getter, nick_getter_type, at_sender
from .help import Help

Help.append_superuser_help("""
【管理命令】
!mute @用户 [原因] [-d 时长] — 禁言用户（默认1小时，0秒解除禁言）
!kick @用户 [原因] [-b] — 踢出用户（-b 并封禁）
!request approve|reject [原因] — 处理加群申请（需回复申请消息）
!delete — 撤回消息（发送即撤回本身；若回复消息则一并撤回回复的消息）
""")

get_user_args = Args["user?", At]["user_id?", int]
reason_args = Args["reason?", str]
duration_option = Option("--duration|-d", Args["v", str])


@Depends
async def parse_user(
    user: Match[At], user_id: Match[int], event: GroupMessageEvent, matcher: Matcher
) -> int:
    if user.available:
        return int(user.result.target)
    if user_id.available:
        return user_id.result
    if event.reply:
        return int(event.reply.sender.user_id or 0)
    await matcher.finish("请指定要操作的用户", at_sender=at_sender(event))


@Depends
def parse_reason(reason: Match[str]) -> str:
    return reason.available and reason.result or "无"


@Depends
def parse_duration(duration: Query[str] = Query("duration.v")) -> str:
    return duration.available and duration.result or "1h"


class AdminPower:
    def __init__(self, group_id: int, bot: Bot):
        self.group_id = group_id
        self.bot = bot

    async def mute(self, user_id: int, duration: str):
        duration_seconds = cast(int, parse(duration))
        await self.bot.set_group_ban(
            group_id=self.group_id, user_id=user_id, duration=duration_seconds
        )
        return duration_seconds

    async def kick(self, user_id: int, ban: bool = False):
        await self.bot.set_group_kick(
            group_id=self.group_id, user_id=user_id, reject_add_request=ban
        )

    async def process_request(
        self, flag: str, sub_type: str, approve: bool, reason: str | None = None
    ):
        await self.bot.set_group_add_request(
            flag=flag, sub_type=sub_type, approve=approve, reason=reason  # type: ignore
        )

    async def delete_message(self, message_id: int):
        await self.bot.delete_msg(message_id=message_id)


@Depends
async def admin(event: GroupMessageEvent, bot: Bot, matcher: Matcher) -> AdminPower:
    data = await bot.get_group_member_info(
        group_id=event.group_id, user_id=event.self_id
    )
    if data["role"] in ("owner", "admin"):
        return AdminPower(event.group_id, bot)
    await matcher.finish(
        "请先给予群主或管理员权限，才能使用该命令", at_sender=at_sender(event)
    )


mute_alconna = Alconna("!mute", get_user_args, reason_args, duration_option)
mute_matcher = on_alconna(
    mute_alconna, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
)


@mute_matcher.handle()
async def mute(
    admin: Annotated[AdminPower, admin],
    user: Annotated[int, parse_user],
    reason: Annotated[str, parse_reason],
    duration: Annotated[str, parse_duration],
    nick_getter: Annotated[nick_getter_type, nick_getter()],
    event: MessageEvent,
):
    duration_seconds = await admin.mute(user, duration)
    nick = await nick_getter(str(user))
    if duration_seconds > 0:
        await mute_matcher.finish(
            f"已禁言 {nick}({user}) {duration_seconds} 秒\n" f"原因：{reason}",
            at_sender=at_sender(event),
        )
    else:
        await mute_matcher.finish(
            f"已解除禁言 {nick}({user})\n" f"原因：{reason}", at_sender=at_sender(event)
        )


kick_alconna = Alconna("!kick", get_user_args, reason_args, Option("--ban|-b"))
kick_matcher = on_alconna(
    kick_alconna, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
)


@kick_matcher.handle()
async def kick(
    admin: Annotated[AdminPower, admin],
    user: Annotated[int, parse_user],
    reason: Annotated[str, parse_reason],
    nick_getter: Annotated[nick_getter_type, nick_getter()],
    event: MessageEvent,
    ban=Query("ban"),
):
    await admin.kick(user, ban.available)
    await kick_matcher.finish(
        f"已踢出 {await nick_getter(str(user))}({user})"
        f"{'并封禁' if ban.available else ''}\n"
        f"原因：{reason}",
        at_sender=at_sender(event),
    )


request_matcher = on_request()


@request_matcher.handle()
async def group_request(
    event: GroupRequestEvent, nick_getter: Annotated[nick_getter_type, nick_getter()]
):
    nick = await nick_getter(str(event.user_id))
    await request_matcher.finish(
        f"f{{{event.flag}}}t{{{event.sub_type}}}\n"
        f"{nick}({event.user_id}) 加群申请\n"
        "回复并发送 !request approve 接受申请，!request reject [reason] 拒绝申请"
    )


process_alconna = Alconna("!request", Args["tp?", str], Args["reason?", str])
process_matcher = on_alconna(
    process_alconna, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER
)


@process_matcher.handle()
async def process_request(
    admin: Annotated[AdminPower, admin],
    tp: Match[str],
    reason: Match[str],
    event: GroupMessageEvent,
):
    # check if reply
    if not event.reply:
        await process_matcher.finish("请回复申请消息", at_sender=at_sender(event))

    # extract flag and sub_type from reply message
    reply_str = event.reply.message.extract_plain_text()
    flag = search(r"f\{(\w+)\}", reply_str)
    sub_type = search(r"t\{(\w+)\}", reply_str)
    if not flag or not sub_type:
        await process_matcher.finish("请回复申请消息", at_sender=at_sender(event))
    flag = flag.group(1)
    sub_type = sub_type.group(1)

    # check if tp is approve or reject
    if not tp.available or tp.result not in ("approve", "reject"):
        await process_matcher.finish(
            "\n用法：!request approve|reject [原因]\n请先回复一条加群申请消息",
            at_sender=at_sender(event),
        )
    approve = tp.result == "approve"
    r = reason.available and reason.result or "无"

    await admin.process_request(flag, sub_type, approve, r)
    await process_matcher.finish(
        f"已{'接受' if approve else '拒绝'}申请\n" f"原因：{r}",
        at_sender=at_sender(event),
    )


delete_matcher = on_command("!delete")


@delete_matcher.handle()
async def delete(admin: Annotated[AdminPower, admin], event: GroupMessageEvent):
    if event.reply:
        await admin.delete_message(event.reply.message_id)
    await admin.delete_message(event.message_id)
    await delete_matcher.finish()
