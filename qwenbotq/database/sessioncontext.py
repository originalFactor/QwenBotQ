# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"会话上下文（AI 对话历史）数据模型"

from beanie import Document
from pydantic import Field

from .utils import noid


class SessionContext(Document):
    "会话持久化 AI 上下文（按会话ID记录）"

    id: str = Field(default_factory=noid)  # 会话ID g{group_id}/u{user_id}
    messages: list[dict] = Field(default_factory=list)  # OpenAI messages 数组
    total_tokens: int = 0  # 当前上下文累计 token 数


async def get_session_context(session_id: str) -> SessionContext:
    "获取指定会话的上下文，不存在则创建并返回"
    rec = await SessionContext.get(session_id)
    if not rec:
        rec = SessionContext(id=session_id)
        await rec.insert()
    return rec


async def replace_session_messages(
    session_id: str, messages: list[dict], total_tokens: int
) -> None:
    "覆盖指定会话的上下文消息与累计 token 数"
    rec = await get_session_context(session_id)
    rec.messages = messages
    rec.total_tokens = total_tokens
    await rec.save()


async def clear_session_context(session_id: str) -> None:
    "清空指定会话的上下文"
    rec = await SessionContext.get(session_id)
    if rec:
        rec.messages = []
        rec.total_tokens = 0
        await rec.save()
