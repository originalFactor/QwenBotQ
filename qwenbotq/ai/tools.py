from collections.abc import Sequence, Mapping

from nonebot.adapters.onebot.v11.event import Reply

from .. import config


def tokenize(messages: Sequence[Mapping[str, str]]) -> int:
    return sum(len(_["content"]) + 4 for _ in messages)


def get_sysprompt(user: str) -> str:
    return (
        config.system_prompt
        if user == "DEFAULT"
        else (
            (config.unsafe_system_prompt or config.system_prompt)
            if user == "UNSAFE"
            else user
        )
    )


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
