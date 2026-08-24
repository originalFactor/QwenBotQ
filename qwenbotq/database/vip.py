# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from datetime import date, timedelta
from time import time

from pydantic import Field
from beanie import Document

from .utils import noid

# VIP 检查结果进程内缓存秒数（购买/续费时自动失效，容忍到期判定最多延迟一个 TTL）
_VIP_CACHE_TTL = 60
# 缓存条目上限，超过即整体清空，避免长期运行无限增长
_VIP_CACHE_MAX = 1024

_vip_cache: dict[str, tuple[float, tuple[bool, date | None]]] = {}


class Vip(Document):
    "VIP用户数据"

    id: str = Field(default_factory=noid)
    expire: date = date.min


async def get_vip(_id: str) -> tuple[bool, date | None]:
    "检查是否为VIP（带短 TTL 进程内缓存，避免每条 AI 消息重复读库）"
    cached = _vip_cache.get(_id)
    if cached is not None and time() - cached[0] < _VIP_CACHE_TTL:
        return cached[1]

    vip = await Vip.get(_id)
    if not vip:
        result: tuple[bool, date | None] = (False, None)
    else:
        result = (vip.expire > date.today(), vip.expire)

    if len(_vip_cache) >= _VIP_CACHE_MAX:
        _vip_cache.clear()
    _vip_cache[_id] = (time(), result)
    return result


async def buy_vip(_id: str, days: int) -> Vip:
    "购买VIP"
    vip = await Vip.get(_id)
    if not vip:
        vip = Vip(id=_id, expire=date.today() + timedelta(days=days))
    else:
        vip.expire = max(vip.expire, date.today()) + timedelta(days=days)
    await vip.save()
    _vip_cache.pop(_id, None)

    return vip
