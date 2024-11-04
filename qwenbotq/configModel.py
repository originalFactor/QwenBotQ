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

from typing import Sequence, Mapping, Union
from pydantic import BaseModel
from nonebot import get_driver


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
    models: Mapping[str, Sequence[Union[float, int]]] = {  # 模型列表（计算方式:Tokens/1000*cost）
        'qwen-max-latest': (0.2, 0.6, 32000),  # (输入价格, 输出价格, 最大上下文)
        'qwen-turbo-latest': (0.003, 0.006, 128000),
        'qwen-plus-latest': (0.008, 0.02, 128000)
    }
    llm_least_coins:int = 0  # 最低使用积分
    set_prompt_cost: int = 1  # 设置提示词价格

    # 个人中心
    daily_sign_max_coins: int = 5  # 每日签到最大获得积分数
    daily_sign_min_coins: int = 1  # 最小
    refresh_price: int = 1  # 换老婆价格
    fork_cost: int = 1  # 导入萝卜数据的价格
    renew_cost: int = 1  # 续费老婆价格
    trusted_wife_source: Sequence[int] = [3003535850, 1297825911]  # 可信的数据导入源

    # 超管
    grant_cost: int = 1  # 授权价格
    bind_cost: int = 1  # 绑定对象价格
    charge_min_perm: int = 1  # 无中生有最低权限等级

