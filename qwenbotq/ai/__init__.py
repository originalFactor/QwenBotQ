# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"AI助手模块"

# Standard imports
from json import dumps
from time import perf_counter
from typing import Annotated, Any, NoReturn
from urllib.error import HTTPError
from datetime import date

# Nonebot imports
from nonebot import on_message, on_command, get_driver
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
)
from arclet.alconna import Alconna, Args, Option, Arparma
from nonebot_plugin_alconna import MultiVar, on_alconna, Match

# Local imports
from .. import config
from ..database import (
    User,
    get_vip,
    Agent,
    get_session_agent,
    set_session_agent,
    get_session_context,
    replace_session_messages,
    clear_session_context,
)
from ..bot_utils import (
    require,
    get_session_id,
    reply_segment,
    at_sender,
    is_group_admin_or_owner,
)
from .tools import get_sysprompt, tokenize, content_to_text, blocked_by_unsafe
from .core import chat
from .summarize import summarize_context
from ..models_dev import autofill_models
from ..help import Help

Help.append_help("""
【AI 助手】
@我 <消息> — 与 AI 对话
设置系统提示词 <名称> — 切换本会话智能体（群聊仅群管/群主，unsafe 仅私聊可用）
更改模型 [模型ID] — 切换 AI 模型
会话信息 — 查看当前会话状态
添加智能体 <名称> <提示词> [选项] — 添加智能体（--unsafe 标记仅私聊可用）
!clear — 清空当前会话上下文（群聊仅群管/群主，私聊仅超级管理员）
!delagent <名称> — 删除智能体（创建者或超级管理员）
!editagent <名称> [选项] — 修改智能体属性（创建者或超级管理员）
!renewvip <会话ID> <天数> — 续期 AI VIP（管理员）
""")

__all__ = []


def strict_to_me(event: MessageEvent, bot: Bot) -> bool:
    return (
        event.message_type == "private"
        or MessageSegment.at(bot.self_id) in event.original_message
    )


def not_from_bot(event: MessageEvent, bot: Bot) -> bool:
    "排除机器人自身发出的消息（如文件/图片回传事件）"
    return str(event.user_id) != bot.self_id


def has_text(event: MessageEvent) -> bool:
    "排除无文本且无图片的内容（纯文件等）"
    return bool(event.get_plaintext().strip()) or bool(event.message["image"])


# 模型未设置 context_length 时的上下文长度回退值（用于触发总结）
FALLBACK_CONTEXT_LENGTH = 8192


def build_user_content(event: MessageEvent, prompt: str) -> tuple[Any, str]:
    "组装本轮 user 内容：回复引用 + 文本 + 图片；返回 (OpenAI content, 文本版用于记忆)"
    parts = []
    if event.reply and event.reply.message:
        reply_text = event.reply.message.extract_plain_text().strip()
        if reply_text:
            parts.append("\n".join(f"> {line}" for line in reply_text.splitlines()))

    images = [
        (seg.data.get("url") or seg.data.get("file") or "").strip()
        for seg in event.message
        if seg.type == "image"
    ]
    images = [u for u in images if u]

    text = "\n\n".join(parts)
    if prompt:
        text = (text + "\n\n" if text else "") + prompt

    if images:
        content: list[dict] = []
        if text:
            content.append({"type": "text", "text": text})
        for url in images:
            content.append({"type": "image_url", "image_url": {"url": url}})
        return content, text
    return text, text


# 大模型回复匹配器
LLMMatcher = on_message(rule=Rule(strict_to_me, not_from_bot, has_text), priority=20)


@LLMMatcher.handle()
async def llm(
    user: Annotated[User, require()],
    event: MessageEvent,
) -> NoReturn:
    "大模型回复"

    assert config.ai

    session_id = get_session_id(event)
    has_vip, _ = await get_vip(session_id)
    if not has_vip:
        await LLMMatcher.finish("\n请先开通 AI VIP !", at_sender=at_sender(event))

    start_time = perf_counter()

    logger.debug(f"Successfully entered llm function with session_id {session_id}")

    # 检查模型是否可用
    t0 = perf_counter()
    models = config.ai.models
    if user.model not in models.keys():
        await user.set({User.model: list(models.keys())[0]})
        await LLMMatcher.send(
            f"\n您所选模型已下线，已自动为您切换可用的 {models[user.model].name} 模型",
            at_sender=at_sender(event),
        )
    logger.debug(
        f"Model check done with {user.model}, cost: {(perf_counter() - t0) * 1000:.2f}ms"
    )

    # 检查是否有效内容（文本或图片）
    t0 = perf_counter()
    prompt = event.get_plaintext().strip()
    if not prompt and not event.message["image"]:
        await LLMMatcher.finish(
            "\n虽然你啥也没说，但是我记住你了！", at_sender=at_sender(event)
        )
    logger.debug(f"Prompt check done!, cost: {(perf_counter() - t0) * 1000:.2f}ms")

    # 读取持久化上下文
    t0 = perf_counter()
    ctx = await get_session_context(session_id)
    messages = ctx.messages
    user_content, user_text = build_user_content(event, prompt)
    messages.append({"role": "user", "content": user_content})

    agent = await get_sysprompt(await get_session_agent(session_id))

    if not agent:
        await set_session_agent(session_id, "DEFAULT")
        await LLMMatcher.send(
            "\n您的系统提示词配置有误，已自动重置为默认提示词。",
            at_sender=at_sender(event),
        )
        agent = await get_sysprompt("DEFAULT")

    assert agent

    if blocked_by_unsafe(agent, session_id):
        await LLMMatcher.finish(
            "\n该智能体仅限私聊会话使用。", at_sender=at_sender(event)
        )

    model = models[user.model]
    predicted_tokens = tokenize(messages)
    logger.debug(f"History construct done!, cost: {(perf_counter() - t0) * 1000:.2f}ms")

    # 检查上下文长度是否足够
    t0 = perf_counter()
    if predicted_tokens > (model.context_length or float("inf")):
        await LLMMatcher.finish(
            f"\n上下文长度 {predicted_tokens} tokens 超过模型能够处理的最长长度 {model.context_length} tokens",
            at_sender=at_sender(event),
        )
    logger.debug(
        f"Context length check done!, cost: {(perf_counter() - t0) * 1000:.2f}ms"
    )

    # 搜索记忆
    if config.ai.memory:
        t0 = perf_counter()
        from .memory import get_memprompt

        agent.prompt += "\n" + await get_memprompt(session_id, user_text)
        logger.debug(f"Memory search done!, cost: {(perf_counter() - t0) * 1000:.2f}ms")

    # 流式回复track
    reply_id = event.message_id
    msgs = []
    para_no = 1
    usage: dict = {}
    chat_start_time = perf_counter()

    try:
        async for paragraph in chat(
            user.model,
            agent.prompt,
            messages,
            agent.temperature,
            agent.frequency_penalty,
            agent.presence_penalty,
            agent.max_tokens,
            agent.thinking,
            usage,
        ):
            logger.debug(f"Sending paragraph {para_no} with reply_id {reply_id}.")
            data = await LLMMatcher.send(reply_segment(reply_id) + paragraph[0])
            reply_id = data["message_id"]
            msgs = paragraph[1]
            para_no += 1

        logger.debug(
            f"Reply done!, chat cost: {(perf_counter() - chat_start_time) * 1000:.2f}ms"
        )

        # 追加上下文并持久化（msgs 含插入到 0 的 system，存储时去掉）
        persist = (
            msgs[1:] if msgs else [m for m in messages if m.get("role") != "system"]
        )
        total_tokens = usage.get("total_tokens")
        if total_tokens is None:
            total_tokens = tokenize(persist)
        await replace_session_messages(session_id, persist, int(total_tokens))

        # 写入记忆（文本序列化）
        if config.ai.memory:
            t0 = perf_counter()
            from .memory import add_memory

            text_msgs = [
                {"role": m.get("role"), "content": content_to_text(m.get("content"))}
                for m in persist
            ]
            await add_memory(session_id, text_msgs)
            logger.debug(f"Memory done!, cost: {(perf_counter() - t0) * 1000:.2f}ms")

        # 达阈值自动总结并覆盖上下文
        if (usage_total := usage.get("total_tokens")) is not None:
            context_length = model.context_length or FALLBACK_CONTEXT_LENGTH
            threshold = int(context_length * config.ai.summarize_threshold)
            if int(usage_total) >= threshold:
                summary = await summarize_context(user.model, persist)
                summarized = [
                    {"role": "user", "content": "（历史对话已总结）\n" + summary}
                ]
                await replace_session_messages(
                    session_id, summarized, tokenize(summarized)
                )
                await LLMMatcher.send(
                    "\n上下文已接近上限，已自动总结历史对话以继续。",
                    at_sender=at_sender(event),
                )

        logger.debug(dumps(persist, ensure_ascii=False, indent=2))
        logger.debug(
            f"llm function total cost: {(perf_counter() - start_time) * 1000:.2f}ms"
        )

        await LLMMatcher.finish()

    except HTTPError as e:
        await LLMMatcher.finish(reply_segment(reply_id) + f"上游异常：{e}")


# 设置系统提示词匹配器
prompt_cmd = Alconna("设置系统提示词", Args["prompt_name?", str])
PromptMatcher = on_alconna(prompt_cmd, block=True)


@PromptMatcher.handle()
async def set_prompt(
    prompt_name: Match[str],
    event: MessageEvent,
) -> NoReturn:
    "设置系统提示词"

    if not prompt_name.available:
        await PromptMatcher.finish(
            "\n用法：设置系统提示词 <智能体名称>\n"
            "可用值：DEFAULT, UNSAFE 或已创建的智能体名称",
            at_sender=at_sender(event),
        )

    session_id = get_session_id(event)

    # 群聊切换会话智能体仅限群管/群主或超级管理员
    if session_id.startswith("g") and (
        event.get_user_id() not in config.supermgr_ids
        and not is_group_admin_or_owner(event)
    ):
        await PromptMatcher.finish(
            "\n仅群管/群主（或超级管理员）可以切换本群智能体。",
            at_sender=at_sender(event),
        )

    agent = await get_sysprompt(prompt_name.result)

    if not agent:
        await PromptMatcher.finish("\n智能体不存在。", at_sender=at_sender(event))

    if blocked_by_unsafe(agent, session_id):
        await PromptMatcher.finish(
            "\n该智能体仅限私聊会话使用。", at_sender=at_sender(event)
        )

    await set_session_agent(session_id, prompt_name.result)
    await PromptMatcher.finish(
        "\n已尝试更新本会话的系统提示词", at_sender=at_sender(event)
    )


# 清空当前会话上下文
ClearContextMatcher = on_command("!clear", block=True)


@ClearContextMatcher.handle()
async def clear_context(
    event: MessageEvent,
) -> NoReturn:
    "清空当前会话上下文（群聊仅群管/群主，私聊仅超级管理员）"

    session_id = get_session_id(event)
    is_superuser = event.get_user_id() in config.supermgr_ids
    if session_id.startswith("g"):
        if not (is_superuser or is_group_admin_or_owner(event)):
            await ClearContextMatcher.finish(
                "\n仅群管/群主（或超级管理员）可以清空本群上下文。",
                at_sender=at_sender(event),
            )
    elif not is_superuser:
        await ClearContextMatcher.finish(
            "\n仅超级管理员可以清空私聊会话的上下文。", at_sender=at_sender(event)
        )

    await clear_session_context(session_id)
    await ClearContextMatcher.finish(
        "\n已清空本会话的上下文。", at_sender=at_sender(event)
    )


@get_driver().on_startup
async def autofill_model_metadata():
    "启动时从 models.dev 补全未填写的模型元数据"
    assert config.ai
    await autofill_models(config.ai.models_dev, config.ai.models)


# 更换模型匹配器
model_cmd = Alconna("更改模型", Args["model_id?", str])
ModelChangeMatcher = on_alconna(model_cmd, block=True)


@ModelChangeMatcher.handle()
async def model_change(
    user: Annotated[User, require()],
    model_id: Match[str],
    event: MessageEvent,
) -> NoReturn:
    "更改模型"

    assert config.ai
    if not model_id.available or model_id.result not in config.ai.models:
        await ModelChangeMatcher.finish(
            "\n请指定一个正确的目标模型。\n支持的模型：\n\n"
            + (
                "\n\n".join(
                    [
                        f"ID: {_[0]}\n"
                        f"名称: {_[1].name}\n"
                        f"最大上下文长度：{_[1].context_length} tokens\n"
                        f"最长输出长度：{_[1].max_tokens} tokens\n"
                        f"简介：{_[1].detail}"
                        for _ in config.ai.models.items()
                    ]
                )
            ),
            at_sender=at_sender(event),
        )
    await user.set({User.model: model_id.result})
    await ModelChangeMatcher.finish("\n成功为您更换模型。", at_sender=at_sender(event))


SessionMatcher = on_command("会话信息", block=True)


@SessionMatcher.handle()
async def session_info(
    event: MessageEvent,
) -> NoReturn:
    "查看会话信息"

    session_id = get_session_id(event)
    vip = await get_vip(session_id)
    await SessionMatcher.finish(
        f"\n会话 ID：{session_id}\n"
        f"VIP 到期：{vip[1].strftime('%Y-%m-%d') if vip[1] and vip[1] > date.today() else '未开通'}",
        at_sender=at_sender(event),
    )


ClearMemoryMatcher = on_command("清除记忆", block=True)


@ClearMemoryMatcher.handle()
async def clear_memory(
    event: MessageEvent,
) -> NoReturn:
    "清除记忆"

    if not config.ai or not config.ai.memory:
        await ClearMemoryMatcher.finish(
            "\n记忆系统未启用。", at_sender=at_sender(event)
        )

    session_id = get_session_id(event)

    if session_id[0] == "g" and event.get_user_id() not in config.supermgr_ids:
        await ClearMemoryMatcher.finish(
            "\n只有超级管理员可以清除群聊会话的记忆。", at_sender=at_sender(event)
        )

    from .memory import clear_memory

    await clear_memory(session_id)
    await ClearMemoryMatcher.finish(
        "\n已尝试清除本会话的记忆", at_sender=at_sender(event)
    )


GetMemoryMatcher = on_command("查看记忆", block=True)


@GetMemoryMatcher.handle()
async def get_memory(
    event: MessageEvent,
) -> NoReturn:
    "查看记忆"

    if not config.ai or not config.ai.memory:
        await GetMemoryMatcher.finish("\n记忆系统未启用。", at_sender=at_sender(event))

    session_id = get_session_id(event)

    if session_id[0] == "g" and event.get_user_id() not in config.supermgr_ids:
        await GetMemoryMatcher.finish(
            "\n只有超级管理员可以查看群聊会话的记忆。", at_sender=at_sender(event)
        )

    from .memory import getall_memory

    memlist = await getall_memory(session_id)
    memstr = "\n".join(memlist)

    await GetMemoryMatcher.finish(
        f"\n当前所有记忆：\n{memstr}", at_sender=at_sender(event)
    )


# 添加智能体匹配器
add_agent_cmd = Alconna(
    "添加智能体",
    Args["agent_name?", str]["prompt?", MultiVar(str)],
    Option("--temperature|-t", Args["temperature", float], help_text="温度参数"),
    Option(
        "--frequency_penalty|-f", Args["frequency_penalty", float], help_text="频率惩罚"
    ),
    Option(
        "--presence_penalty|-p", Args["presence_penalty", float], help_text="存在惩罚"
    ),
    Option("--max_tokens|-m", Args["max_tokens", int], help_text="最大输出长度"),
    Option("--thinking|-T", Args["thinking", bool], help_text="是否开启思考模式"),
    Option(
        "--unsafe|-u",
        Args["unsafe", bool],
        help_text="是否标记为unsafe（仅限私聊会话使用）",
    ),
)
AddAgentMatcher = on_alconna(add_agent_cmd, block=True)


@AddAgentMatcher.handle()
async def add_agent(
    user: Annotated[User, require()],
    agent_name: Match[str],
    prompt: Match[tuple[str, ...]],
    arp: Arparma[Any],
    event: MessageEvent,
) -> NoReturn:
    "添加智能体"

    if not agent_name.available or not prompt.available:
        await AddAgentMatcher.finish(
            "\n用法：添加智能体 <名称> <提示词> [选项]\n"
            "选项：\n"
            "  -t/--temperature <值> —— 温度参数 (默认1.0)\n"
            "  -f/--frequency_penalty <值> —— 频率惩罚 (默认0.0)\n"
            "  -p/--presence_penalty <值> —— 存在惩罚 (默认0.0)\n"
            "  -m/--max_tokens <值> —— 最大输出长度\n"
            "  -T/--thinking —— 是否开启思考模式 (默认False)\n"
            "  -u/--unsafe <值> —— 标记为 unsafe（仅限私聊会话使用，默认False)\n",
            at_sender=at_sender(event),
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await AddAgentMatcher.finish(
            "\n不允许使用保留名称。", at_sender=at_sender(event)
        )

    existing = await Agent.get(agent_name.result)
    if existing:
        await AddAgentMatcher.finish("\n该智能体已存在。", at_sender=at_sender(event))

    agent = Agent(id=agent_name.result, prompt=" ".join(prompt.result))
    agent.owner = user.id
    if (t := arp.query[float]("temperature.temperature")) is not None:
        agent.temperature = t
    if (f := arp.query[float]("frequency_penalty.frequency_penalty")) is not None:
        agent.frequency_penalty = f
    if (p := arp.query[float]("presence_penalty.presence_penalty")) is not None:
        agent.presence_penalty = p
    if (m := arp.query[int]("max_tokens.max_tokens")) is not None:
        agent.max_tokens = m
    if (t := arp.query[bool]("thinking.thinking")) is not None:
        agent.thinking = t
    if (u := arp.query[bool]("unsafe.unsafe")) is not None:
        agent.unsafe = u
    await agent.insert()
    await AddAgentMatcher.finish(
        f"\n已成功添加智能体 {agent_name.result}",
        at_sender=at_sender(event),
    )


# 删除智能体匹配器
del_agent_cmd = Alconna("!delagent", Args["agent_name?", str])
DelAgentMatcher = on_alconna(del_agent_cmd, block=True)


@DelAgentMatcher.handle()
async def del_agent(
    user: Annotated[User, require()],
    agent_name: Match[str],
    event: MessageEvent,
) -> NoReturn:
    "删除智能体"

    if not agent_name.available:
        await DelAgentMatcher.finish(
            "\n用法：!delagent <名称>",
            at_sender=at_sender(event),
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await DelAgentMatcher.finish(
            "\n不允许删除保留智能体。", at_sender=at_sender(event)
        )

    agent = await Agent.get(agent_name.result)
    if not agent:
        await DelAgentMatcher.finish("\n该智能体不存在。", at_sender=at_sender(event))

    if not (user.id in config.supermgr_ids or (agent.owner and agent.owner == user.id)):
        await DelAgentMatcher.finish(
            "\n您没有权限管理该智能体。", at_sender=at_sender(event)
        )

    await agent.delete()
    await DelAgentMatcher.finish(
        f"\n已成功删除智能体 {agent_name.result}",
        at_sender=at_sender(event),
    )


# 修改智能体匹配器
edit_agent_cmd = Alconna(
    "!editagent",
    Args["agent_name?", str],
    Option("--prompt", Args["prompt", MultiVar(str)], help_text="提示词"),
    Option("--temperature|-t", Args["temperature", float], help_text="温度参数"),
    Option(
        "--frequency_penalty|-f", Args["frequency_penalty", float], help_text="频率惩罚"
    ),
    Option(
        "--presence_penalty|-p", Args["presence_penalty", float], help_text="存在惩罚"
    ),
    Option("--max_tokens|-m", Args["max_tokens", int], help_text="最大输出长度"),
    Option("--thinking|-T", Args["thinking", bool], help_text="是否开启思考模式"),
    Option(
        "--unsafe|-u",
        Args["unsafe", bool],
        help_text="是否标记为unsafe（仅限私聊会话使用）",
    ),
)
EditAgentMatcher = on_alconna(edit_agent_cmd, block=True)


@EditAgentMatcher.handle()
async def edit_agent(
    user: Annotated[User, require()],
    agent_name: Match[str],
    arp: Arparma[Any],
    event: MessageEvent,
) -> NoReturn:
    "修改智能体"

    if not agent_name.available:
        await EditAgentMatcher.finish(
            "\n用法：!editagent <名称> [选项]\n"
            "选项：\n"
            "  --prompt <提示词> —— 修改提示词\n"
            "  -t/--temperature <值> —— 温度参数\n"
            "  -f/--frequency_penalty <值> —— 频率惩罚\n"
            "  -p/--presence_penalty <值> —— 存在惩罚\n"
            "  -m/--max_tokens <值> —— 最大输出长度\n"
            "  -T/--thinking —— 是否开启思考模式 (默认False)\n"
            "  -u/--unsafe <值> —— 标记为 unsafe（仅限私聊会话使用，默认False)\n",
            at_sender=at_sender(event),
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await EditAgentMatcher.finish(
            "\n不允许修改保留智能体。", at_sender=at_sender(event)
        )

    agent = await Agent.get(agent_name.result)
    if not agent:
        await EditAgentMatcher.finish("\n该智能体不存在。", at_sender=at_sender(event))

    if not (user.id in config.supermgr_ids or (agent.owner and agent.owner == user.id)):
        await EditAgentMatcher.finish(
            "\n您没有权限管理该智能体。", at_sender=at_sender(event)
        )

    updates: dict[str, str | float | int | bool] = {}
    if (pr := arp.query[tuple[str, ...]]("prompt.prompt")) is not None:
        updates["prompt"] = " ".join(pr)
    if (t := arp.query[float]("temperature.temperature")) is not None:
        updates["temperature"] = t
    if (f := arp.query[float]("frequency_penalty.frequency_penalty")) is not None:
        updates["frequency_penalty"] = f
    if (p := arp.query[float]("presence_penalty.presence_penalty")) is not None:
        updates["presence_penalty"] = p
    if (m := arp.query[int]("max_tokens.max_tokens")) is not None:
        updates["max_tokens"] = m
    if (t := arp.query[bool]("thinking.thinking")) is not None:
        updates["thinking"] = t
    if (u := arp.query[bool]("unsafe.unsafe")) is not None:
        updates["unsafe"] = u

    if not updates:
        await EditAgentMatcher.finish(
            "\n请至少指定一个要修改的选项。", at_sender=at_sender(event)
        )

    await agent.set(updates)
    await EditAgentMatcher.finish(
        f"\n已成功修改智能体 {agent_name.result}，"
        f"更新了：{', '.join(updates.keys())}",
        at_sender=at_sender(event),
    )
