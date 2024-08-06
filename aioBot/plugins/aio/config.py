from pydantic import BaseModel
from typing import List
from nonebot import get_driver

class Config(BaseModel):
    mongo_uri : str = 'mongodb://127.0.0.1:27017'
    mongo_db : str = 'aioBot'
    dashscope_api_key : str
    supermgr_ids : List[str] = list(get_driver().config.superusers)
    system_prompt : str = 'You are a smart assistant.'
    daily_sign_max_coins : int = 5
    daily_sign_min_coins : int = 1
    refresh_price : int = 1
