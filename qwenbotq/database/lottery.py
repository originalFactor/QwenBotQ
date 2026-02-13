# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"抽奖数据模型"

from typing import Annotated

from beanie import Document, Indexed


class LotteryTicket(Document):
    "抽奖票据"

    user_id: Annotated[str, Indexed(unique=True)]
    number: Annotated[str, Indexed(unique=True)]
