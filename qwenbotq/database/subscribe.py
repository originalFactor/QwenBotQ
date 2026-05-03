# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"订阅模型"

from pydantic import Field
from beanie import Document

from .utils import noid


class SubscribeStatus(Document):
    "订阅状态"

    id: int = Field(default_factory=noid)
    last_update: int = 0
    living: bool = False
