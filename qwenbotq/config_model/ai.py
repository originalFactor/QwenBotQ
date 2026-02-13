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
    name: str = "Unknown"
    context_length: int | None = None
    max_tokens: int | None = None
    detail: str = ""


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


class MemoryModelConfig(BaseModel):
    "记忆嵌入器配置"

    api_id: str
    model: str
    dimensions: int | None = None


class MemoryConfig(BaseModel):
    "记忆配置"

    llm: MemoryModelConfig
    reranker: MemoryModelConfig | None = None
    embedder: MemoryModelConfig
    threshold: float = 0.8


class LLMConfig(BaseModel):
    "大模型配置"

    apis: dict[str, LLMApiConfig]
    models: dict[str, LLMModelConfig]
    default_prompts: DefaultPromptsConfig = DefaultPromptsConfig()
    tools: LLMToolsConfig = LLMToolsConfig()
    memory: MemoryConfig | None = None
