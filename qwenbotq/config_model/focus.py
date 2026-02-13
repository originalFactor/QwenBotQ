# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
哔哩哔哩动态订阅配置模型
"""

from pydantic import BaseModel


class Focus(BaseModel):
    "订阅"

    uid: str
    groups: list[str] = []
    users: list[str] = []


class FocusOptions(BaseModel):
    "订阅选项"

    sessdata: str
    subscribes: list[Focus]
    interval: dict[str, int] = {"hours": 1}
