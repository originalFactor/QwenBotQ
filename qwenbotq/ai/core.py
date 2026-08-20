# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk
from httpx2 import AsyncClient

from .. import config
from .calls import get_tool_prompts, calling_vacumm, process_calls


async def chat(
    model: str,
    system: str,
    messages: list[dict],
    temperature: float,
    frequency_penalty: float,
    presence_penalty: float,
    max_tokens: int | None,
    thinking: bool,
) -> AsyncGenerator[tuple[str, list[dict]], Any]:
    assert config.ai

    model_obj = config.ai.models[model]
    api = config.ai.apis[model_obj.api_id]
    tools = get_tool_prompts()
    messages.insert(0, {"role": "system", "content": system})

    async with AsyncClient() as httpClient:
        openai = AsyncOpenAI(
            base_url=api.base, api_key=api.token, http_client=httpClient
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
                    user="QwenBotQ",
                )
            )

            # 处理回复
            received = ""
            full_received = ""
            callings = {}

            async for chunk in response:
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
