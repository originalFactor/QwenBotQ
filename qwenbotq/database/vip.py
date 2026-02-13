from datetime import date, timedelta

from pydantic import Field
from beanie import Document

from .utils import noid


class Vip(Document):
    "VIP用户数据"

    id: str = Field(default_factory=noid)
    expire: date = date.min


async def get_vip(_id: str) -> tuple[bool, date | None]:
    "检查是否为VIP"
    vip = await Vip.get(_id)
    if not vip:
        return False, None
    return vip.expire > date.today(), vip.expire


async def buy_vip(_id: str, days: int) -> Vip:
    "购买VIP"
    vip = await Vip.get(_id)
    if not vip:
        vip = Vip(id=_id, expire=date.today() + timedelta(days=days))
    else:
        vip.expire = max(vip.expire, date.today()) + timedelta(days=days)
    await vip.save()

    return vip
