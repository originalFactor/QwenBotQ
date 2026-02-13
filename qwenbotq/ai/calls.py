from collections.abc import Iterable
from json import loads, dumps

from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall

from .. import config
from .funcs import web_search


def get_tool_prompts() -> list[dict]:
    tools = []

    if config.ai and config.ai.tools.bocha:
        tools.append(web_search.WEB_SEARCH_PROMPT)

    return tools


def calling_vacumm(cache: dict, delta: Iterable[ChoiceDeltaToolCall]) -> None:
    for chunk in delta:
        if chunk.index not in cache:
            cache[chunk.index] = {
                "id": "",
                "type": "function",
                "function": {"name": "", "arguments": ""},
            }

        if chunk.id:
            cache[chunk.index]["id"] += chunk.id

        function = chunk.function

        if function:
            if function.name:
                cache[chunk.index]["function"]["name"] += function.name

            if function.arguments:
                cache[chunk.index]["function"]["arguments"] += function.arguments


async def process_calls(calls: Iterable[dict]) -> list[dict[str, str]]:
    r = []
    for call in calls:
        name = call["function"]["name"]
        id = call["id"]
        arguments = loads(call["function"]["arguments"])

        result = ""
        match name:
            case "web_search":
                result = dumps(await web_search.web_search(**arguments))
            case _:
                result = "函数不存在"

        r.append({"role": "tool", "tool_call_id": id, "name": name, "content": result})
    return r
