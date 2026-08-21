# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"本子搜索结果状态数据模型（下一页依赖会话记忆）"

from beanie import Document
from pydantic import Field

from .utils import noid


class SearchState(Document):
    "本子搜索结果状态（按会话ID记录）"

    id: str = Field(default_factory=noid)  # 会话ID g{group_id}/u{user_id}
    query: str = ""  # 搜索关键词
    limit: int = 5  # 展示条目数
    exh: bool = False  # 是否使用 ExHentai
    next: int = 0  # 下一页搜索偏移（上一页最后一个画廊ID）


async def get_search_state(session_id: str) -> SearchState | None:
    "获取指定会话的本子搜索状态，无记录返回 None"
    return await SearchState.get(session_id)


async def set_search_state(
    session_id: str,
    query: str,
    limit: int,
    exh: bool,
    next: int,
) -> None:
    "保存指定会话的本子搜索状态"
    rec = await SearchState.get(session_id)
    if not rec:
        rec = SearchState(id=session_id, query=query, limit=limit, exh=exh, next=next)
    else:
        rec.query, rec.limit, rec.exh, rec.next = query, limit, exh, next
    await rec.save()


async def clear_search_state(session_id: str) -> None:
    "清空指定会话的本子搜索状态"
    rec = await SearchState.get(session_id)
    if rec:
        await rec.delete()
