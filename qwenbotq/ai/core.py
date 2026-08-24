# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk
from httpx2 import AsyncClient
from nonebot import get_driver

from .. import config
from .calls import get_tool_prompts, calling_vacumm, process_calls

# 进程级共享 HTTP 客户端：复用连接池，避免每次回复重建 TCP/TLS 连接
_http_client: AsyncClient | None = None


def _get_http_client() -> AsyncClient:
    global _http_client
    if _http_client is None:
        _http_client = AsyncClient()
    return _http_client


@get_driver().on_shutdown
async def _close_http_client() -> None:
    "关闭共享 HTTP 客户端"
    if _http_client is not None:
        await _http_client.aclose()


async def chat(
    model: str,
    system: str,
    messages: list[dict],
    temperature: float,
    frequency_penalty: float,
    presence_penalty: float,
    max_tokens: int | None,
    thinking: bool,
    usage: dict | None = None,
) -> AsyncGenerator[tuple[str, list[dict]], Any]:
    assert config.ai

    model_obj = config.ai.models[model]
    api = config.ai.apis[model_obj.api_id]
    tools = get_tool_prompts()
    messages.insert(0, {"role": "system", "content": system})

    openai = AsyncOpenAI(
        base_url=api.base, api_key=api.token, http_client=_get_http_client()
    )
    while True:

        # 创建请求
        response: AsyncStream[ChatCompletionChunk] = (
            await openai.chat.completions.create(
                model=model_obj.model_id,
                messages=messages,  # type: ignore
                tools=tools,  # type: ignore
                max_tokens=max_tokens or model_obj.max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=True,
                extra_body={
                    "thinking": {"type": "enabled" if thinking else "disabled"}
                },
                stream_options={"include_usage": True},
                user="QwenBotQ",
            )
        )

        # 处理回复
        received = ""
        full_received = ""
        callings = {}

        async for chunk in response:
            # 记录实际使用量（流式末尾 chunk 携带 usage）
            if usage is not None and chunk.usage is not None:
                usage["prompt_tokens"] = chunk.usage.prompt_tokens
                usage["completion_tokens"] = chunk.usage.completion_tokens
                usage["total_tokens"] = chunk.usage.total_tokens

            # 有数据
            if not chunk.choices:
                continue

            # 加入数据
            delta = chunk.choices[0].delta

            # 处理函数调用
            calling_vacumm(callings, delta.tool_calls or [])

            # 处理文本信息
            recv_len = len(received)
            received += delta.content or ""
            full_received += delta.content or ""

            # 寻找段落分隔符
            while (sep := received.find("\n\n", recv_len - 2)) != -1:
                if p := received[: sep + 1].replace("\\~", "").strip():
                    yield (p, messages)
                received = received[sep + 1 :]

        messages.append(
            {
                "role": "assistant",
                "content": full_received,
                "tool_calls": list(callings.values()),
            }
        )
        received = received.replace("\\~", "").strip()
        if received:
            yield (received, messages)
        if not callings:
            break
        messages += await process_calls(callings.values())
