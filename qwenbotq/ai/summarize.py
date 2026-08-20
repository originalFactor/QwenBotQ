# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"上下文自动总结"

from openai import AsyncOpenAI
from httpx2 import AsyncClient

from .. import config
from .tools import content_to_text

SUMMARIZE_SYSTEM = (
    "你是一个负责压缩对话历史的助手。请阅读以下用户与 AI 的对话，"
    "用简洁但完整的中文总结出：关键信息、用户的偏好与要求、已经完成和正在进行的事情、"
    "以及任何之后继续对话需要记住的要点。直接输出总结正文，不要其他解释。"
)


async def summarize_context(model: str, messages: list[dict]) -> str:
    "调用模型把历史对话总结为一段紧凑摘要"
    assert config.ai

    model_obj = config.ai.models[model]
    api = config.ai.apis[model_obj.api_id]

    text = "\n\n".join(
        f"[{m.get('role', '')}]: {content_to_text(m.get('content'))}" for m in messages
    )

    async with AsyncClient() as httpClient:
        openai = AsyncOpenAI(
            base_url=api.base, api_key=api.token, http_client=httpClient
        )
        resp = await openai.chat.completions.create(
            model=model_obj.model_id,
            messages=[
                {"role": "system", "content": SUMMARIZE_SYSTEM},
                {"role": "user", "content": f"以下是需要总结的对话历史：\n\n{text}"},
            ],
            temperature=0.5,
        )
    return resp.choices[0].message.content or ""
