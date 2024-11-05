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

'数据库模块'

# standard import
from typing import Optional, Sequence, Dict
from datetime import date, timedelta

# third-party import
from nonebot import get_driver
from nonebot.log import logger
from beanie import Document, Indexed, init_beanie
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

# local import
from . import config


class Mongo:
    'nonebot_plugin_mongodb 修复内嵌版'
    _client: AsyncIOMotorClient = None

    @classmethod
    def client(cls) -> AsyncIOMotorClient:
        "MongoDB 客户端"
        if cls._client:
            return cls._client
        try:
            logger.info("正在初始化MongoDB客户端...")
            cls._client = AsyncIOMotorClient(config.mongo_uri)
        except Exception as e:
            raise RuntimeError("MongoDB客户端初始化失败") from e
        # if cls._client.get(plugin_config.mongo_database_name)

    @classmethod
    async def register_models(cls, document_models: Sequence[Document]):
        '注册模型'
        cls.client()
        database = getattr(cls._client, config.mongo_db)
        await init_beanie(database, document_models=document_models)


class Binded(BaseModel):
    '绑定用户'
    id: str
    expire: date


class User(Document):
    '用户文档'
    id: Indexed(str)  # type: ignore
    nick: str = 'Unknown'
    permission: int = 0
    system_prompt: str = config.system_prompt
    coins: int = 0
    sign_expire: date = date.min
    model: str = list(config.models.keys())[0]
    binded: Optional[Binded] = None
    profile_expire: date = date.min


async def apply_bind(a: User, b: User) -> date:
    '应用一个绑定'
    expire = date.today()+timedelta(1)
    a.binded = Binded(id=b.id, expire=expire)
    b.binded = Binded(id=a.id, expire=expire)
    return expire


@get_driver().on_startup
async def initialize_database():
    '初始化数据库'

    # 引擎初始化

    document_models = Document.__subclasses__()
    if not document_models:
        raise RuntimeError("没有有效的文档子类")

    # 检查重复模型
    document_names: Dict[str, str] = {}
    for cls in document_models:
        cls_path = f"{cls.__module__}.{cls.__name__}"
        try:
            cls_name = cls.Settings.name.lower()
        except AttributeError:
            cls_name = cls.__name__.lower()
        if cls_name in document_names:
            clashed_cls_path = document_names[cls_name]
            raise RuntimeError(
                f"重复的文档子类: {cls_name} 来自 {cls_path} 和 {clashed_cls_path}"
            )
        else:
            document_names[cls_name] = cls_path

    logger.debug(
        "正在初始化MongoDB文档:\n"
        + "\n".join(
            [
                f"{cls_name} (来自 {cls_path})"
                for cls_name, cls_path in document_names.items()
            ]
        )
    )

    await Mongo.register_models(document_models)


    # 初始化管理员
    for superuser in config.supermgr_ids:
        if not await User.get(superuser):
            await User(id=superuser, permission=3).insert()
