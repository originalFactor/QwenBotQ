# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"图片缓存功能"

# standard imports
import base64
import os
import time
import zipfile
from os.path import isdir, isfile
from uuid import uuid4

# external imports
import httpx
from bson import ObjectId
from nonebot import get_driver, on_command, on_message, on_notice
from nonebot.adapters.onebot.v11 import (
    Bot,
    FriendRecallNoticeEvent,
    GroupRecallNoticeEvent,
    Message,
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
from .bot_utils import at_sender
from .database.recalloffset import get_recall_offset, set_recall_offset
from .help import Help

__all__ = []

Help.append_superuser_help("""
【撤回图片】
!getrecalls — 获取已读偏移之后的新撤回图片（多条一并发送）
!getrecallszip — 将已读偏移之后的新撤回图片打包为zip获取
!setrecalloffset <偏移> — 手动指定已读偏移
!delrecalls — 删除当前保存的所有已撤回图片并重置已读偏移
""")

# 缓存目录与保留天数
CACHE_DIR = "downloads/cache"  # 正常缓存目录
RECALLED_DIR = "downloads/recalled"  # 消息被撤回后单独保留的目录
EXPIRE_DAYS = 2  # 缓存过期天数
CLEAN_INTERVAL = 3600  # 清理任务轮询间隔（秒）


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
    "缓存所有图片消息中的原图"

    images = event.message["image"]
    if not images:
        return

    for seg in images:
        data = seg.data
        url = data.get("url")  # type: ignore[union-attr]
        if not url:
            continue

        # 文件名含消息ID便于撤回时匹配；扩展名固定为 jpg
        path = f"{CACHE_DIR}/{event.message_id}_{uuid4().hex}.jpg"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                content = (await client.get(url)).content
            with open(path, "wb") as f:
                f.write(content)
            logger.debug(f"已缓存图片 {path}（消息 {event.message_id}）")
        except Exception as e:
            logger.warning(f"图片缓存失败（消息 {event.message_id}）：{e}")


# 撤回事件匹配器
RecallMatcher = on_notice(priority=1, block=False)


@RecallMatcher.handle()
async def on_recall(event) -> None:
    "消息被撤回时，将对应缓存图片转移到单独文件夹（不删除）"

    if not isinstance(event, (GroupRecallNoticeEvent, FriendRecallNoticeEvent)):
        return

    prefix = f"{event.message_id}_"
    moved: list[str] = []
    for f in os.listdir(CACHE_DIR):
        if not f.startswith(prefix):
            continue
        old = os.path.join(CACHE_DIR, f)
        if not isfile(old):
            continue
        # 重命名为 ObjectId，避免文件名带 message_id 导致的排序顺序问题；其字典序即时间序（进程内单调）
        new = os.path.join(RECALLED_DIR, f"{str(ObjectId())}.jpg")
        try:
            os.rename(old, new)
            moved.append(new)
        except OSError as e:
            logger.warning(f"转移撤回图片失败（消息 {event.message_id}）：{e}")

    if moved:
        logger.debug(
            f"消息 {event.message_id} 被撤回，已转移图片到 {RECALLED_DIR}: {moved}"
        )


async def cleanup_cache() -> None:
    "按文件修改时间删除超过保留天数的未撤回缓存图片"

    cutoff = time.time() - EXPIRE_DAYS * 86400
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
    logger.info(f"图片缓存功能已启用，缓存目录：{CACHE_DIR}，清理间隔：{CLEAN_INTERVAL}s")


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
    "获取已读偏移之后的新撤回图片；以多条图片一并发送"

    files = sorted(
        f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))
    )
    offset = await get_recall_offset(str(event.user_id))
    new_files = files[offset:]

    if not new_files:
        await GetRecallsMatcher.finish(
            f"\n暂无新的撤回图片（当前已读偏移 {offset}/{len(files)}）",
            at_sender=at_sender(event),
        )

    # 内联 base64 图片，无需服务器，跨机器亦可
    msg = Message()
    for f in new_files:
        with open(os.path.join(RECALLED_DIR, f), "rb") as fh:
            data = base64.b64encode(fh.read()).decode()
        msg += MessageSegment.image(f"base64://{data}")

    await GetRecallsMatcher.send(msg, at_sender=at_sender(event))
    await set_recall_offset(str(event.user_id), len(files))
    await GetRecallsMatcher.finish(
        f"\n已发送 {len(new_files)} 张撤回图片；新偏移 {len(files)}",
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
        f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))
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
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in new_files:
                zf.write(os.path.join(RECALLED_DIR, f), arcname=f)
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
        f"\n已将 {len(new_files)} 张撤回图片打包上传；新偏移 {len(files)}",
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
    "删除所有已撤回图片，并将已读偏移重置为 0"

    deleted = 0
    for f in os.listdir(RECALLED_DIR):
        p = os.path.join(RECALLED_DIR, f)
        if isfile(p):
            os.remove(p)
            deleted += 1

    await set_recall_offset(str(event.user_id), 0)
    await DelRecallsMatcher.finish(
        f"\n已删除 {deleted} 张撤回图片，已读偏移已重置为 0",
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
