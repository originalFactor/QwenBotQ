# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"图片缓存数据模型"

from datetime import datetime

from beanie import Document
from pydantic import Field


class ImageCache(Document):
    "图片缓存记录"

    message_id: int = 0  # 所属消息ID，用于撤回匹配
    path: str = ""  # 缓存文件路径
    recalled: bool = False  # 是否已因消息撤回而转移到单独文件夹
    created_at: datetime = Field(default_factory=datetime.now)  # 缓存创建时间