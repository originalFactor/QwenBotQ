# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from mem0 import AsyncMemory, AsyncMemoryClient
from nonebot import get_driver
from nonebot.log import logger

from qwenbotq.config_model.ai import CloudMemoryConfig

from .. import config
from ..help import HELP_TEXT

HELP_TEXT += """
清除记忆 — 清除当前会话记忆
查看记忆 — 查看当前会话记忆
"""

assert config.ai and config.ai.memory

memconf = config.ai.memory
memory: AsyncMemory | AsyncMemoryClient | None = None

if isinstance(memconf, CloudMemoryConfig):
    memory = AsyncMemoryClient(memconf.api_key)
else:
    conf = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": memconf.qdrant.collection_name,
                "host": memconf.qdrant.host,
                "port": memconf.qdrant.port,
                "embedding_model_dims": memconf.embedder.dimensions,
            },
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": memconf.llm.model_id,
                "api_key": config.ai.apis[memconf.llm.api_id].token,
                "openai_base_url": config.ai.apis[memconf.llm.api_id].base,
            },
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": memconf.embedder.model_id,
                "api_key": config.ai.apis[memconf.embedder.api_id].token,
                "embedding_dims": memconf.embedder.dimensions,
                "openai_base_url": config.ai.apis[memconf.embedder.api_id].base,
            },
        },
    }
    if memconf.reranker:
        conf["reranker"] = {
            "provider": "llm_reranker",
            "config": {
                "provider": "openai",
                "model": memconf.reranker.model_id,
                "api_key": config.ai.apis[memconf.reranker.api_id].token,
                "openai_base_url": config.ai.apis[memconf.reranker.api_id].base,
            },
        }




async def get_memprompt(session_id: str, prompt: str) -> str:
    "获取记忆提示词"

    assert memory
    results = await memory.search(
        prompt, user_id=session_id, threshold=memconf.threshold
    )
    return "MEMORIES: \n" + "\n".join([r["memory"] for r in results["results"]])


async def add_memory(session_id: str, messages: list[dict]):
    "添加记忆"

    assert memory
    await memory.add(
        messages,
        user_id=session_id,
    )


async def clear_memory(session_id: str):
    "清除记忆"

    assert memory
    await memory.delete_all(user_id=session_id)


async def getall_memory(session_id: str) -> list[str]:
    "获取所有记忆"

    assert memory
    results = await memory.get_all(user_id=session_id)
    return [r["memory"] for r in results["results"]]


@get_driver().on_startup
async def initialize_memory():
    "初始化记忆系统"
    if isinstance(memconf, CloudMemoryConfig):
        logger.info("使用云记忆系统")
        return

    global memory
    logger.info("正在初始化记忆系统...")
    logger.debug(f"记忆系统配置: {conf}")
    memory = await AsyncMemory.from_config(conf)
