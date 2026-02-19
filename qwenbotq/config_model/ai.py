# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"大模型配置模型"

from pydantic import BaseModel


class AgentLike(BaseModel):
    prompt: str
    temperature: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: int | None = None


class LLMApiConfig(BaseModel):
    "LLM API"

    base: str
    token: str


class LLMModelConfig(BaseModel):
    "LLM Model"

    api_id: str
    model_id: str
    name: str = "Unknown"
    context_length: int | None = None
    max_tokens: int | None = None
    detail: str = ""
    dimensions: int | None = None


class BoChaAPIConfig(BaseModel):
    "博查API配置"

    endpoint: str = "https://api.bocha.cn/v1/web-search"
    token: str


class LLMToolsConfig(BaseModel):
    "LLM Tools"

    bocha: BoChaAPIConfig | None = None


class DefaultPromptsConfig(BaseModel):
    "默认提示词配置"

    default: AgentLike = AgentLike(
        prompt="你是我的人工智能助手，请根据我的要求提供帮助。"
    )
    unsafe: AgentLike | None = None


class MemoryQdrantConfig(BaseModel):
    "Qdrant向量数据库配置"

    collection_name: str = "aioBotMemories"
    host: str = "127.0.0.1"
    port: int = 6333


class MemoryConfig(BaseModel):
    "记忆配置"

    llm: LLMModelConfig
    reranker: LLMModelConfig | None = None
    embedder: LLMModelConfig
    qdrant: MemoryQdrantConfig = MemoryQdrantConfig()
    threshold: float = 0.8


class LLMConfig(BaseModel):
    "大模型配置"

    apis: dict[str, LLMApiConfig]
    models: dict[str, LLMModelConfig]
    default_prompts: DefaultPromptsConfig = DefaultPromptsConfig()
    tools: LLMToolsConfig = LLMToolsConfig()
    memory: MemoryConfig | None = None
