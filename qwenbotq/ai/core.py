from dataclasses import dataclass
from math import ceil
from collections.abc import AsyncGenerator
from typing import Any

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk

from .. import config, httpClient
from .calls import get_tool_prompts, calling_vacumm, process_calls
from .funcs.update_memory import get_memory

SYSPROMPT_APPEND = """
注意：
1. 你是一个聊天机器人，你的回复应该较简短，符合即时通讯的需求。
2. 你可以通过双换行分段，分段后该段落会被提前发送。你可以用分段的方式来发送较长的内容而避免用户等待过长时间。
3. 因此你应该避免在应连续的内容中插入双换行，导致奇怪的分段效果。你可以通过在两个换行间插入 `\\~` 来避免这个问题，例如 `\\n\\~\\n` 。
"""


@dataclass
class ChatReturn:
    paragraph: str
    cost: int


async def chat(
    model: str,
    system: str,
    messages: list[dict],
    temperature: float,
    frequency_penalty: float,
    presence_penalty: float,
    session_id: str,
) -> AsyncGenerator[ChatReturn, Any]:
    model_obj = config.models[model]
    api = config.apis[model_obj.api_id]

    openai = AsyncOpenAI(
        base_url=api.base_uri, api_key=api.token, http_client=httpClient
    )

    tools = get_tool_prompts()

    total_usage_after = 0

    while True:
        book = f'\n\n小本本：\n```txt\n{await get_memory(session_id)}\n```'
        sys_msg = {"role": "system", "content": SYSPROMPT_APPEND + system + book}

        # 创建请求
        response: AsyncStream[ChatCompletionChunk] = (
            await openai.chat.completions.create(
                model=model,
                messages=[sys_msg] + messages,  # type: ignore
                tools=tools,  # type: ignore
                max_tokens=model_obj.max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=True,
            )
        )

        # 处理回复
        usage_after = 0
        received = ""
        full_received = ""
        callings = {}

        async for chunk in response:
            # 更新用量
            if chunk.usage:
                usage_after = ceil(
                    (
                        chunk.usage.prompt_tokens * model_obj.input_cost
                        + chunk.usage.completion_tokens * model_obj.output_cost
                    )
                    / 1000
                )

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
                    yield ChatReturn(paragraph=p, cost=total_usage_after + usage_after)
                received = received[sep + 1 :]

        total_usage_after += usage_after

        received = received.replace("\\~", "").strip()
        if received:
            yield ChatReturn(paragraph=received, cost=total_usage_after)

        if not callings:
            break

        messages.append(
            {
                "role": "assistant",
                "content": full_received,
                "tool_calls": list(callings.values()),
            }
        )

        messages += await process_calls(callings.values(), session_id)
