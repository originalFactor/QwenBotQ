# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"图片缓存功能"

# standard imports
import asyncio
import os
import zipfile
from os.path import isdir, isfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# external imports
import httpx
from nonebot import on_message, on_notice, on_command, get_driver
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
    Bot,
    GroupRecallNoticeEvent,
    FriendRecallNoticeEvent,
)

# local imports
from . import config
from .help import Help
from .database.imagecache import ImageCache

__all__ = []

Help.append_superuser_help(
    """
【撤回图片】
getrecalls — 获取当前保存的所有已撤回图片
delrecalls — 删除当前保存的所有已撤回图片
"""
)

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

        ext = Path(url.split("?")[0]).suffix or ".img"
        rec = ImageCache(message_id=event.message_id)
        await rec.insert()

        path = f"{CACHE_DIR}/{rec.id}{ext}"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                content = (await client.get(url)).content
            with open(path, "wb") as f:
                f.write(content)
            rec.path = path
            await rec.save()
            logger.debug(f"已缓存图片 {path}（消息 {event.message_id}）")
        except Exception as e:
            logger.warning(f"图片缓存失败（消息 {event.message_id}）：{e}")
            await rec.delete()


# 撤回事件匹配器
RecallMatcher = on_notice(priority=1, block=False)


@RecallMatcher.handle()
async def on_recall(event) -> None:
    "消息被撤回时，将对应缓存图片转移到单独文件夹（不删除）"

    if not isinstance(event, (GroupRecallNoticeEvent, FriendRecallNoticeEvent)):
        return

    moved: list[str] = []
    async for rec in ImageCache.find({"message_id": event.message_id}):
        if rec.recalled:
            continue
        old = rec.path
        new = f"{RECALLED_DIR}/{Path(old).name}"
        try:
            if isfile(old):
                os.rename(old, new)
            rec.recalled = True
            rec.path = new
            await rec.save()
            moved.append(new)
        except Exception as e:
            logger.warning(f"转移撤回图片失败（消息 {event.message_id}）：{e}")

    if moved:
        logger.debug(
            f"消息 {event.message_id} 被撤回，已转移图片到 {RECALLED_DIR}: {moved}"
        )


async def cleanup_expired() -> None:
    "删除超过保留天数的未撤回缓存图片"

    cutoff = datetime.now() - timedelta(days=EXPIRE_DAYS)
    async for rec in ImageCache.find({"recalled": False, "created_at": {"$lt": cutoff}}):
        try:
            if rec.path and isfile(rec.path):
                os.remove(rec.path)
            await rec.delete()
        except Exception as e:
            logger.warning(f"删除过期缓存图片失败（{rec.path}）：{e}")


async def _cleanup_loop() -> None:
    "周期清理过期缓存图片"
    while True:
        try:
            await cleanup_expired()
        except Exception as e:
            logger.warning(f"清理图片缓存任务失败：{e}")
        await asyncio.sleep(CLEAN_INTERVAL)


@get_driver().on_startup
async def _start_cleanup() -> None:
    "启动清理任务"
    asyncio.create_task(_cleanup_loop())
    logger.info("图片缓存功能已启用，缓存目录：%s", CACHE_DIR)


# ===== SUPERUSER 私聊管理命令 =====
_private_rule = Rule(lambda event: isinstance(event, PrivateMessageEvent))

# getrecalls：获取当前保存的所有已撤回图片
GetRecallsMatcher = on_command(
    "getrecalls",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@GetRecallsMatcher.handle()
async def get_recalls(bot: Bot, event: PrivateMessageEvent) -> None:
    "发送所有已撤回图片；多张自动打包为 zip 上传"

    files = sorted(
        f for f in os.listdir(RECALLED_DIR) if isfile(os.path.join(RECALLED_DIR, f))
    )
    if not files:
        await GetRecallsMatcher.finish("\n暂无已撤回的图片", at_sender=True)

    host = config.imagesearch.remote_host
    port = config.imagesearch.remote_port or config.imagesearch.file_server_port

    # 单张图片直接发送
    if len(files) == 1:
        url = f"http://{host}:{port}/recalled/{files[0]}"
        await GetRecallsMatcher.send(MessageSegment.image(url), at_sender=True)
        await GetRecallsMatcher.finish("\n已发送该撤回图片", at_sender=True)

    # 多张图片打包 zip 后作为文件上传
    zip_name = f"recalls_{uuid4().hex}.zip"
    zip_path = os.path.join("downloads", zip_name)
    try:
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in files:
                zf.write(os.path.join(RECALLED_DIR, f), arcname=f)
        await bot.upload_private_file(
            user_id=event.user_id,
            file=f"http://{host}:{port}/{zip_name}",
            name="recalls.zip",
        )
    finally:
        if os.path.isfile(zip_path):
            os.remove(zip_path)

    await GetRecallsMatcher.finish(
        f"\n已将 {len(files)} 张撤回图片打包上传", at_sender=True
    )


# delrecalls：删除当前保存的所有已撤回图片
DelRecallsMatcher = on_command(
    "delrecalls",
    rule=_private_rule,
    permission=SUPERUSER,
    priority=1,
    block=True,
)


@DelRecallsMatcher.handle()
async def del_recalls(event: PrivateMessageEvent) -> None:
    "删除所有已撤回图片"

    deleted = 0
    for f in os.listdir(RECALLED_DIR):
        p = os.path.join(RECALLED_DIR, f)
        if isfile(p):
            os.remove(p)
            deleted += 1

    # 同步删除数据库中的撤回记录
    await ImageCache.find({"recalled": True}).delete()

    await DelRecallsMatcher.finish(f"\n已删除 {deleted} 张撤回图片", at_sender=True)