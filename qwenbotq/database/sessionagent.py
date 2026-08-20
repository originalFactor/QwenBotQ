# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"会话智能体绑定数据模型"

from beanie import Document
from pydantic import Field

from .utils import noid


class SessionAgent(Document):
    "会话智能体绑定（按会话ID记录）"

    id: str = Field(default_factory=noid)  # 会话ID g{group_id}/u{user_id}
    agent: str = "DEFAULT"  # 当前智能体名称


async def get_session_agent(session_id: str) -> str:
    "获取指定会话的当前智能体名称"
    rec = await SessionAgent.get(session_id)
    return rec.agent if rec else "DEFAULT"


async def set_session_agent(session_id: str, agent: str) -> None:
    "设置指定会话的当前智能体名称"
    rec = await SessionAgent.get(session_id)
    if not rec:
        rec = SessionAgent(id=session_id, agent=agent)
    else:
        rec.agent = agent
    await rec.save()
