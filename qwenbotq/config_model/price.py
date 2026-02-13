"价格配置模型"

from pydantic import BaseModel


class PriceConfig(BaseModel):
    daily_sign_max_coins: int = 50  # 每日签到最大获得积分数
    daily_sign_min_coins: int = 1  # 最小
    refresh_price: int = 1  # 换老婆价格
    renew_cost: int = 1  # 续费老婆价格
