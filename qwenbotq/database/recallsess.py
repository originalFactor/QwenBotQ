# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"撤回图片监听会话数据模型"

from beanie import Document
from pydantic import Field

from .utils import noid


class RecallSessions(Document):
    "待监听的撤回图片会话ID集合"

    id: str = Field(default_factory=noid)  # 固定键
    sessions: list[str] = Field(default_factory=list)  # 会话ID列表


_KEY = "recall_sessions"

# 进程内缓存：避免每条消息都查库；监听列表仅由 add/remove 修改，变更时失效
_sessions_cache: set[str] | None = None


def _invalidate_sessions_cache() -> None:
    "监听会话列表变更后失效缓存"
    global _sessions_cache
    _sessions_cache = None


async def get_recall_sessions() -> set[str]:
    "获取所有监听会话ID（带进程内缓存）"
    global _sessions_cache
    if _sessions_cache is None:
        rec = await RecallSessions.get(_KEY)
        _sessions_cache = set(rec.sessions) if rec else set()
    return _sessions_cache


async def add_recall_session(sess_id: str) -> bool:
    "添加监听会话，返回是否确实新增"
    rec = await RecallSessions.get(_KEY)
    if not rec:
        rec = RecallSessions(id=_KEY, sessions=[sess_id])
        await rec.save()
        _invalidate_sessions_cache()
        return True
    if sess_id in rec.sessions:
        return False
    rec.sessions.append(sess_id)
    await rec.save()
    _invalidate_sessions_cache()
    return True


async def remove_recall_session(sess_id: str) -> bool:
    "移除监听会话，返回是否确实移除"
    rec = await RecallSessions.get(_KEY)
    if not rec or sess_id not in rec.sessions:
        return False
    rec.sessions.remove(sess_id)
    await rec.save()
    _invalidate_sessions_cache()
    return True
