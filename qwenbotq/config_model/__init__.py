# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"The config module of QwenBotQ."

from pydantic import BaseModel
from yaml import safe_load

from .. import driver
from .ai import LLMConfig
from .database import DatabaseConfig
from .focus import FocusOptions
from .price import PriceConfig
from .lottery import LotteryConfig


class Config(BaseModel):
    """The config class of QwenBotQ."""

    supermgr_ids: list[str] = list(
        driver.config.superusers
    )  # 超管列表，自动从Nonebot读取
    database: DatabaseConfig = DatabaseConfig()  # 数据库
    ai: LLMConfig | None = None  # 大模型配置
    price: PriceConfig = PriceConfig()  # 价格配置
    focus: FocusOptions | None = None  # 关注配置
    lottery: LotteryConfig = LotteryConfig()  # 抽奖配置


def get_config() -> Config:
    """Get the config of QwenBotQ."""

    with open("config.yml", encoding="utf-8") as f:
        data = safe_load(f)
    return Config.model_validate(data)
