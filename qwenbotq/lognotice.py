# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"日志告警：将 WARNING 及以上级别日志自动转发到所有超管私聊"

# standard imports
import asyncio
from collections import deque
from time import time

# external imports
from nonebot import get_bot, get_driver
from nonebot.log import logger

# internal imports
from . import config

__all__ = []

# 本模块自身产生的日志不再回送，避免无限递归
_MODULE_NAME = __name__
# 同 (name, message) 在窗口内仅发送一次，避免重复错误刷屏
_DEDUP_WINDOW = 5.0

# 启动后捕获的事件循环引用；跨线程调度异步转发时使用
_loop: asyncio.AbstractEventLoop | None = None
# 去重队列：(name, message, ts)
_recent: deque[tuple[str, str, float]] = deque()


def _should_dedup(name: str, message: str) -> bool:
    "窗口内已发送过相同 (name, message) 则返回 True（跳过本次）"
    now = time()
    while _recent and now - _recent[0][2] > _DEDUP_WINDOW:
        _recent.popleft()
    for n, m, _ in _recent:
        if n == name and m == message:
            return True
    _recent.append((name, message, now))
    return False


async def _forward(level: str, name: str, message: str) -> None:
    "向所有超管私聊转发一条告警；失败时仍记录日志，但本模块日志会被 sink 跳过转发，避免递归"
    try:
        bot = get_bot()
    except ValueError:
        logger.warning("日志告警转发跳过：机器人尚未连接或存在多个连接")
        return
    text = f"[日志告警] {level} | {name}\n{message}"
    for sid in config.supermgr_ids:
        if not sid:
            continue
        try:
            await bot.send_msg(user_id=int(sid), message=text)
        except Exception as e:
            # 记录到日志以供排查；record["name"] 为本模块，会被 _is_self_log 跳过转发，故不递归
            logger.warning(f"日志告警转发失败（超管 {sid}）：{e}")


def _is_self_log(record) -> bool:  # type: ignore[no-untyped-def]
    "判断是否本模块自身产生的日志（用于过滤递归）"
    name = record["name"] or ""
    return name == _MODULE_NAME or name.startswith(_MODULE_NAME + ".")


def _sink(message) -> None:  # type: ignore[no-untyped-def]
    "loguru 同步 sink：过滤本模块日志、去重后跨线程调度异步转发"
    record = message.record
    name = record["name"] or ""
    if _is_self_log(record):
        return
    text = record["message"]
    exc = record["exception"]
    if exc is not None:
        text += f"\n{exc.type.__name__}: {exc.value}"
    if _should_dedup(name, text):
        return
    if _loop is None:
        return
    asyncio.run_coroutine_threadsafe(_forward(record["level"].name, name, text), _loop)


@get_driver().on_startup
async def _register_log_sink() -> None:
    "启动时捕获事件循环并注册日志告警 sink"
    global _loop
    _loop = asyncio.get_running_loop()
    logger.add(_sink, level="WARNING", filter=lambda record: not _is_self_log(record))
    logger.info("日志告警已启用：WARNING 及以上日志将自动转发到超管私聊")
