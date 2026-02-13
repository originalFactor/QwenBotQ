from collections.abc import Sequence, Mapping

from nonebot.adapters.onebot.v11.event import Reply

from .. import config
from ..database import Agent
from ..config_model.ai import AgentLike


async def get_sysprompt(id: str) -> Agent | AgentLike | None:
    "获取系统提示词"

    assert config.ai

    if id == "DEFAULT":
        return config.ai.default_prompts.default.model_copy()
    if id == "UNSAFE":
        return (
            config.ai.default_prompts.unsafe or config.ai.default_prompts.default
        ).model_copy()

    agent = await Agent.get(id)
    if agent:
        return agent
    return None


def tokenize(messages: Sequence[Mapping[str, str]]) -> int:
    return sum(len(_["content"]) + 4 for _ in messages)


def construct_history(replies: Sequence[Reply], self_id: int) -> list[dict[str, str]]:
    messages = []
    last_role: str | None = None
    for r in replies:
        content = r.message.extract_plain_text().strip()
        if not content:
            continue
        if content.startswith("\u200b"):
            continue
        role = "assistant" if r.sender.user_id == self_id else "user"
        if last_role == role:
            messages[-1]["content"] += "\n\n" + content
            continue
        messages.append({"role": role, "content": content})
        last_role = role
    return messages
