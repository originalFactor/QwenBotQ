"抽奖数据模型"

from typing import Annotated

from beanie import Document, Indexed


class LotteryTicket(Document):
    "抽奖票据"

    user_id: Annotated[str, Indexed(unique=True)]
    number: Annotated[str, Indexed(unique=True)]
