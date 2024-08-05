from pydantic import BaseModel, field_validator, Field
from typing import Union

class Config(BaseModel):
    mongo_uri : str = 'mongodb://127.0.0.1:27017'
    mongo_db : str = 'aioBot'
    dashscope_api_key : str
    supermgr_id : str
    system_prompt : str = 'You are a smart assistant.'
    system_reset_command : str = 'initialize'
    daily_sign_max_coins : int = 5
    daily_sign_min_coins : int = 1
    refresh_price : int = 1

    @field_validator('supermgr_id')
    @classmethod
    def validate_supermgr_id(cls, v:Union[str, int])->str:
        if isinstance(v, int):
            v = str(v)
        return v