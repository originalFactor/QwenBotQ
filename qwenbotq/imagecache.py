# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"图片缓存功能"

# standard imports
import asyncio
import os
import time
import zipfile
from os.path import isdir, isfile
from uuid import uuid4

# external imports
import httpx
from nonebot import get_driver, on_command, on_message, on_notice
from nonebot.adapters.onebot.v11 import (
    Bot,
    FriendRecallNoticeEvent,
    GroupRecallNoticeEvent,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot_plugin_apscheduler import scheduler

# local imports
from . import config
from .bot_utils import at_sender, get_session_id
from .database.recalloffset import get_recall_offset, set_recall_offset
from .database.recallsess import (
    add_recall_session,
    get_recall_sessions,
    remove_recall_session,
)
from .help import Help

__all__ = []

Help.append_superuser_help("""
【撤回图片】
!listenrecalls <sessionId> — 添加监听撤回图片的会话（群 g{群号} / 私聊 u{QQ号}）
!listlistening — 查看当前监听会话
!dellistening <sessionId> — 移除指定监听会话
!getrecalls — 获取已读偏移之后的新撤回图片（逐张内联发送）
!getrecallszip — 将已读偏移之后的新撤回图片打包为zip获取
!setrecalloffset <偏移> — 手动指定已读偏移
!delrecalls — 删除当前保存的所有已撤回图片并重置已读偏移
""")

# 缓存目录与保留秒数
CACHE_DIR = "downloads/cache"  # 正常缓存目录
RECALLED_DIR = "downloads/recalled"  # 消息被撤回后单独保留的目录
EXPIRE_SECONDS = 300  # 缓存过期秒数（5 分钟）
CLEAN_INTERVAL = 300  # 清理任务轮询间隔（秒）


def _ensure_dirs() -> None:
    "确保缓存目录存在"
    for d in (CACHE_DIR, RECALLED_DIR):
        if not isdir(d):
            os.makedirs(d)


_ensure_dirs()

# 图片缓存匹配器：优先级高于AI等阻塞匹配器，但不打断后续处理
ImageCacheMatcher = on_message(priority=5, block=False)


@ImageCacheMatcher.handle()
async def cache_images(event: MessageEvent) -> None:
    "仅缓存监听会话内图片消息的原图"

    if get_session_id(event) not in await get_recall_sessions():
        return

    images = event.message["image"]
    if not images:
        return

    for seg in images:
        data = seg.data
        # sub_type == 1 或含 emoji_id 为表情包，不缓存；参数不存在视为正常图片
        if data.get("sub_type") == 1 or "emoji_id" in data:  # type: ignore[union-attr]
            continue
        url = data.get("url")  # type: ignore[union-attr]
        if not url:
            continue

        # 文件名含消息ID便于撤回时匹配；扩展名固定为 jpg
        path = os.path.join(CACHE_DIR, f"{event.message_id}_{uuid4().hex}.jpg")
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                content = resp.content
            if not content:
                raise ValueError("下载内容为空")
            with open(path, "wb") as f:
                f.write(content)
            logger.debug(f"已缓存图片 {path}（消息 {event.message_id}）")
        except Exception as e:
            logger.warning(f"图片缓存失败（消息 {event.message_id}）：{e}")
            # 清理可能已写入的异常文件（0 字节或半成品），避免后续误当作有效图片
            if isfile(path):
                try:
                    os.remove(path)
                except OSError as ce:
                    logger.warning(f"清理异常缓存文件失败（{path}）：{ce}")


# 撤回事件匹配器
RecallMatcher = on_notice(priority=1, block=False)


@RecallMatcher.handle()
async def on_recall(event) -> None:
    "消息被撤回时，将对应缓存图片转移到单独文件夹（不删除），仅监听指定会话"

    if not isinstance(event, (GroupRecallNoticeEvent, FriendRecallNoticeEvent)):
        return

    # 会话ID：群 → g{group_id}，好友 → u{user_id}
    if isinstance(event, GroupRecallNoticeEvent):
        sess = f"g{event.group_id}"
    else:
        sess = f"u{event.user_id}"
    if sess not in await get_recall_sessions():
        return

    prefix = f"{event.message_id}_"
    moved: list[str] = []
    for f in os.listdir(CACHE_DIR):
        if not f.startswith(prefix):
            continue
        old = os.path.join(CACHE_DIR, f)
        if not isfile(old):
            continue
        # 不重命名，原文件名直接移动到独立目录；读取时按修改时间排序
        new = os.path.join(RECALLED_DIR, f)
        try:
            os.rename(old, new)
            moved.append(new)
        except OSError as e:
            logger.warning(f"转移撤回图片失败（消息 {event.message_id}）：{e}")

    if moved:
        logger.debug(
            f"消息 {event.message_id} 被撤回，已转移图片到 {RECALLED_DIR}: {moved}"
        )


def _pack_recalls_zip(new_files: list[str], zip_path: str) -> int:
    "同步打包撤回图片为 zip（在事件循环外执行，避免阻塞消息处理）；返回跳过的 0 字节文件数"
    skipped = 0
    with zipfile.ZipFile(zip_path, "w") as zf:
        for f in new_files:
            path = os.path.join(RECALLED_DIR, f)
            if os.path.getsize(path) == 0:
                logger.warning(f"撤回图片为 0 字节，跳过：{f}")
                skipped += 1
                continue
            zf.write(path, arcname=f)
    return skipped


async def cleanup_cache() -> None:
    "按文件修改时间删除超过保留秒数的未撤回缓存图片"

    cutoff = time.time() - EXPIRE_SECONDS
    for f in os.listdir(CACHE_DIR):
        p = os.path.join(CACHE_DIR, f)
        if not isfile(p) or os.path.getmtime(p) >= cutoff:
            continue
        try:
            os.remove(p)
        except OSError as e:
            logger.warning(f"删除过期缓存图片失败（{p}）：{e}")


@get_driver().on_startup
async def _register_cleanup_job() -> None:
    "注册图片缓存清理定时任务，并先执行一次"
    await cleanup_cache()
    scheduler.add_job(
        cleanup_cache,
        "interval",
        seconds=CLEAN_INTERVAL,
        id="imagecache_cleanup",
        replace_existing=True,
    )
    logger.info(
        f"图片缓存功能已启用，缓存目录：{CACHE_DIR}，清理间隔：{CLEAN_INTERVAL}s"
    )


# ===== SUPERUSER 私聊管理命令 =====
_private_rule = Rule(lambda event: isinstance(event, PrivateMessageEvent))

# !getrecalls：获取当前保存的所有已撤回图片
GetRecallsMatcher = on_command(
    "!getrecalls",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@GetRecallsMatcher.handle()
async def get_recalls(event: PrivateMessageEvent) -> None:
    "获取已读偏移之后的新撤回图片；逐张内联发送以避开单条消息体积/数量限制"

    files = sorted(
        (f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))),
        key=lambda f: os.path.getmtime(os.path.join(RECALLED_DIR, f)),
    )
    offset = await get_recall_offset(str(event.user_id))
    new_files = files[offset:]

    if not new_files:
        await GetRecallsMatcher.finish(
            f"\n暂无新的撤回图片（当前已读偏移 {offset}/{len(files)}）",
            at_sender=at_sender(event),
        )

    # 直接传 bytes，适配器内部编码为 base64 内联发送；无需服务器，跨机器亦可；逐张发送以避开单条消息体积/数量限制
    sent = 0
    skipped = 0
    for f in new_files:
        path = os.path.join(RECALLED_DIR, f)
        # 跳过 0 字节等异常文件，但仍计入偏移推进，避免下次重复处理
        if os.path.getsize(path) == 0:
            logger.warning(f"撤回图片为 0 字节，跳过：{f}")
            skipped += 1
            continue
        try:
            with open(path, "rb") as fh:
                data = fh.read()
            await GetRecallsMatcher.send(
                MessageSegment.image(data),
                at_sender=at_sender(event),
            )
            sent += 1
        except Exception as e:
            logger.warning(f"发送撤回图片失败（{f}）：{e}")
            # 中途失败：仅将偏移推进到已处理位置（已发送 + 已跳过），避免下次重复发送
            await set_recall_offset(str(event.user_id), offset + sent + skipped)
            await GetRecallsMatcher.finish(
                f"\n发送中断：已发送 {sent}，跳过 {skipped}，"
                f"剩余 {len(new_files) - sent - skipped}（{e}）",
                at_sender=at_sender(event),
            )

    await set_recall_offset(str(event.user_id), len(files))
    await GetRecallsMatcher.finish(
        f"\n已发送 {sent} 张撤回图片"
        + (f"（跳过 {skipped} 张异常）" if skipped else "")
        + f"；新偏移 {len(files)}",
        at_sender=at_sender(event),
    )


# !getrecallszip：将新撤回图片打包为 zip 获取
GetRecallsZipMatcher = on_command(
    "!getrecallszip",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@GetRecallsZipMatcher.handle()
async def get_recalls_zip(bot: Bot, event: PrivateMessageEvent) -> None:
    "获取已读偏移之后的新撤回图片；打包为 zip 上传"

    files = sorted(
        (f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))),
        key=lambda f: os.path.getmtime(os.path.join(RECALLED_DIR, f)),
    )
    offset = await get_recall_offset(str(event.user_id))
    new_files = files[offset:]

    if not new_files:
        await GetRecallsZipMatcher.finish(
            f"\n暂无新的撤回图片（当前已读偏移 {offset}/{len(files)}）",
            at_sender=at_sender(event),
        )

    # 与图片搜索一致：使用全局可达的文件服务器地址供 OneBot 拉取（跨机器）
    host = config.fileserver.remote_host
    port = config.fileserver.remote_port or config.fileserver.file_server_port

    zip_name = f"recalls_{uuid4().hex}.zip"
    zip_path = os.path.join("downloads", zip_name)
    try:
        # 打包在事件循环外执行（线程池），避免大文件压缩阻塞全部消息处理
        skipped = await asyncio.to_thread(_pack_recalls_zip, new_files, zip_path)
        await bot.upload_private_file(
            user_id=event.user_id,
            file=f"http://{host}:{port}/{zip_name}",
            name="recalls.zip",
        )
        await set_recall_offset(str(event.user_id), len(files))
    finally:
        if os.path.isfile(zip_path):
            os.remove(zip_path)

    await GetRecallsZipMatcher.finish(
        f"\n已将 {len(new_files) - skipped} 张撤回图片打包上传"
        + (f"（跳过 {skipped} 张异常）" if skipped else "")
        + f"；新偏移 {len(files)}",
        at_sender=at_sender(event),
    )


# !delrecalls：删除当前保存的所有已撤回图片
DelRecallsMatcher = on_command(
    "!delrecalls",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@DelRecallsMatcher.handle()
async def del_recalls(event: PrivateMessageEvent) -> None:
    "删除所有已撤回图片，并将已读偏移重置为 0；仅当已读全部文件时允许"

    files = [
        f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))
    ]
    offset = await get_recall_offset(str(event.user_id))

    if offset < len(files):
        await DelRecallsMatcher.finish(
            f"\n尚未读完全部撤回图片（已读偏移 {offset}/{len(files)}），拒绝删除，请先使用 !getrecalls 或 !getrecallszip 读完",
            at_sender=at_sender(event),
        )

    for f in files:
        os.remove(os.path.join(RECALLED_DIR, f))

    await set_recall_offset(str(event.user_id), 0)
    await DelRecallsMatcher.finish(
        f"\n已删除 {len(files)} 张撤回图片，已读偏移已重置为 0",
        at_sender=at_sender(event),
    )


# !setrecalloffset：手动指定已读偏移
SetRecallOffsetMatcher = on_command(
    "!setrecalloffset",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@SetRecallOffsetMatcher.handle()
async def set_recall_offset_cmd(event: PrivateMessageEvent) -> None:
    "手动指定已读偏移"

    parts = event.get_plaintext().strip().split()
    if len(parts) < 2:
        await SetRecallOffsetMatcher.finish(
            "\n用法：!setrecalloffset <偏移>", at_sender=at_sender(event)
        )

    try:
        offset = int(parts[-1])
    except ValueError:
        await SetRecallOffsetMatcher.finish(
            "\n偏移必须是整数", at_sender=at_sender(event)
        )

    if offset < 0:
        await SetRecallOffsetMatcher.finish(
            "\n偏移不能为负数", at_sender=at_sender(event)
        )

    await set_recall_offset(str(event.user_id), offset)
    await SetRecallOffsetMatcher.finish(
        f"\n已将已读偏移设为 {offset}", at_sender=at_sender(event)
    )


# !listenrecalls：添加监听会话
ListenRecallsMatcher = on_command(
    "!listenrecalls",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@ListenRecallsMatcher.handle()
async def listen_recalls(event: PrivateMessageEvent) -> None:
    "添加监听撤回图片的会话"

    parts = event.get_plaintext().strip().split()
    if len(parts) < 2 or not parts[-1]:
        await ListenRecallsMatcher.finish(
            "\n用法：!listenrecalls <sessionId>（群 g{群号} / 私聊 u{QQ号}）",
            at_sender=at_sender(event),
        )

    sess = parts[-1]
    added = await add_recall_session(sess)
    if added:
        await ListenRecallsMatcher.finish(
            f"\n已监听会话 {sess}", at_sender=at_sender(event)
        )
    else:
        await ListenRecallsMatcher.finish(
            f"\n会话 {sess} 已在监听列表中", at_sender=at_sender(event)
        )


# !listlistening：查看当前监听会话
ListListeningMatcher = on_command(
    "!listlistening",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@ListListeningMatcher.handle()
async def list_listening(event: PrivateMessageEvent) -> None:
    "查看当前监听会话"

    sessions = await get_recall_sessions()
    if not sessions:
        await ListListeningMatcher.finish(
            "\n当前未监听任何会话", at_sender=at_sender(event)
        )
    await ListListeningMatcher.finish(
        "\n当前监听会话：\n" + "\n".join(sorted(sessions)),
        at_sender=at_sender(event),
    )


# !dellistening：移除指定监听会话
DelListeningMatcher = on_command(
    "!dellistening",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@DelListeningMatcher.handle()
async def del_listening(event: PrivateMessageEvent) -> None:
    "移除指定监听会话"

    parts = event.get_plaintext().strip().split()
    if len(parts) < 2 or not parts[-1]:
        await DelListeningMatcher.finish(
            "\n用法：!dellistening <sessionId>", at_sender=at_sender(event)
        )

    sess = parts[-1]
    removed = await remove_recall_session(sess)
    if removed:
        await DelListeningMatcher.finish(
            f"\n已移除监听会话 {sess}", at_sender=at_sender(event)
        )
    else:
        await DelListeningMatcher.finish(
            f"\n会话 {sess} 不在监听列表中", at_sender=at_sender(event)
        )
