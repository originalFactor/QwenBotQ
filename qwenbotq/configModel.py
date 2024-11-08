# Copyright (C) 2024 originalFactor
#
# This file is part of QwenBotQ.
#
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

'The config module of QwenBotQ.'

from typing import Sequence, Mapping, Optional, Union
from pydantic import BaseModel
from nonebot import get_driver


class Model(BaseModel):
    name: str = 'Unknown'
    input_cost: float = 0
    output_cost: float = 0
    max_tokens: Optional[int] = None
    detail: str = ''

class Focus(BaseModel):
    uid: str
    groups: Sequence[str] = []
    users: Sequence[str] = []

class FocusOptions(BaseModel):
    sessdata: str
    subscribes: Sequence[Focus]
    interval: Mapping[str, int] = {
        'hours': 1
    }


class Config(BaseModel):

    '''The config class of QwenBotQ.'''

    # 通用
    supermgr_ids: Sequence[str] = list(
        get_driver().config.superusers
    )  # 超管列表，自动从Nonebot读取

    # 数据库
    mongo_uri: str = 'mongodb://127.0.0.1:27017'  # 数据库地址
    mongo_db: str = 'aioBot'  # 数据库名

    # 大模型
    base_url: str = 'https://dashscope.aliyuncs.com/compatible-mode/v1'  # OpenAI格式接口地址
    api_key: str  # OpenAI format API Key
    system_prompt: str = 'You are a smart assistant.'  # 默认系统提示词
    models: Mapping[str, Model] = {  # 模型价格
        'qwen-max': Model(
            name='通义千问-Max',
            input_cost=2, 
            output_cost=6, 
            max_tokens=30720,
            detail='通义千问系列效果最好的模型，适合复杂、多步骤的任务。'
        ),
        'qwen-plus': Model(
            name='通义千问-Plus',
            input_cost=0.08, 
            output_cost=0.02, 
            max_tokens=129024,
            detail='能力均衡，推理效果、成本和速度介于通义千问-Max和通义千问-Turbo之间，适合中等复杂任务。'
        ),
        'qwen-turbo': Model(
            name='通义千问-Turbo',
            input_cost=0.03, 
            output_cost=0.06, 
            max_tokens=129024,
            detail='通义千问系列速度最快、成本很低的模型，适合简单任务。'
        ),
        'qwen-long': Model(
            name='通义千问-Long',
            input_cost=0.05,
            output_cost=0.2,
            max_tokens=10000000,
            detail='支持总结和分析长达千万字的文档，且成本极低。'
        )
    }
    set_prompt_cost: int = 1  # 设置提示词价格

    # 个人中心
    daily_sign_max_coins: int = 5  # 每日签到最大获得积分数
    daily_sign_min_coins: int = 1  # 最小
    refresh_price: int = 1  # 换老婆价格
    fork_cost: int = 1  # 导入萝卜数据的价格
    renew_cost: int = 1  # 续费老婆价格
    trusted_wife_source: Sequence[str] = ["3003535850", "1297825911"]  # 可信的数据导入源

    # 超管
    grant_cost: int = 1  # 授权价格
    bind_cost: int = 1  # 绑定对象价格
    charge_min_perm: int = 1  # 无中生有最低权限等级

    # BiliBili 动态关注
    focus: Optional[FocusOptions] = None
