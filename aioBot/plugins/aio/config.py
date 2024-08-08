from pydantic import BaseModel
from typing import List
from nonebot import get_driver

class Config(BaseModel):
    mongo_uri : str = 'mongodb://127.0.0.1:27017' # 数据库地址
    mongo_db : str = 'aioBot' # 数据库名
    dashscope_api_key : str # 通义千问API Key
    supermgr_ids : List[str] = list(get_driver().config.superusers) # 超管列表，自动从Nonebot读取
    system_prompt : str = 'You are a smart assistant.' # 默认系统提示词
    daily_sign_max_coins : int = 5 # 每日签到最大获得积分数
    daily_sign_min_coins : int = 1 # 最小
    refresh_price : int = 1 # 换老婆价格
    llm_cost : int = 1 # 通义千问价格
    grant_cost : int = 1 # 授权价格
    set_prompt_cost : int = 1 # 设置提示词价格
    bind_cost : int = 1 # 绑定对象价格
    charge_min_perm : int = 1 # 无中生有最低权限等级
