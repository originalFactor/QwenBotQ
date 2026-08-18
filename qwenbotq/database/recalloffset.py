# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"已撤回图片读取进度数据模型"

from beanie import Document
from pydantic import Field

from .utils import noid


class RecallOffset(Document):
    "已撤回图片读取进度（按超管用户记录）"

    id: str = Field(default_factory=noid)  # 超管用户ID
    offset: int = 0  # 已读取的图片数量偏移


async def get_recall_offset(user_id: str) -> int:
    "获取指定用户的已读偏移"
    rec = await RecallOffset.get(user_id)
    return rec.offset if rec else 0


async def set_recall_offset(user_id: str, offset: int) -> None:
    "设置指定用户的已读偏移"
    rec = await RecallOffset.get(user_id)
    if not rec:
        rec = RecallOffset(id=user_id, offset=offset)
    else:
        rec.offset = offset
    await rec.save()
