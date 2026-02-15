# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


"AI助手模块"


# Standard imports
from json import dumps
from typing import Annotated, Any
from urllib.error import HTTPError
from collections.abc import Sequence
from datetime import date

# Nonebot imports
from nonebot import on_message
from nonebot.log import logger
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    MessageSegment,
)
from nonebot.adapters.onebot.v11.event import Reply
from arclet.alconna import Alconna, Args, Option, Arparma
from nonebot_plugin_alconna import on_alconna, Match

# Local imports
from .. import config
from ..database import User, get_vip, Agent
from ..bot_utils import require, get_flow_replies, get_session_id
from .tools import get_sysprompt, construct_history, tokenize
from .core import chat


# 大模型回复匹配器
LLMMatcher = on_message(to_me(), priority=20)


@LLMMatcher.handle()
async def llm(
    user: Annotated[User, require()],
    replies: Annotated[Sequence[Reply] | None, get_flow_replies],
    bot: Bot,
    event: MessageEvent,
):
    "大模型回复"

    assert config.ai

    session_id = get_session_id(event)

    logger.debug(f"Successfully entered llm function with session_id {session_id}")

    # 检查模型是否可用
    models = config.ai.models
    if user.model not in models.keys():
        await user.set({User.model: list(models.keys())[0]})
        await LLMMatcher.send(
            f"\n您所选模型已下线，已自动为您切换可用的 {models[user.model].name} 模型",
            at_sender=True,
        )
    
    logger.debug(f"Model check done with {user.model}")

    # 检查是否有提示词
    prompt = event.get_plaintext().strip()
    if not prompt:
        await LLMMatcher.finish("\n虽然你啥也没说，但是我记住你了！", at_sender=True)

    logger.debug(f"Prompt check done!")

    # 构建历史消息
    system_prompt = await get_sysprompt(user.system_prompt)

    if not system_prompt:
        await user.set({User.system_prompt: "DEFAULT"})
        await LLMMatcher.send(
            "\n您的系统提示词配置有误，已自动重置为默认提示词。", at_sender=True
        )
        system_prompt = await get_sysprompt("DEFAULT")

    assert system_prompt

    messages = construct_history(replies or [], int(bot.self_id))
    messages.append({"role": "user", "content": prompt})

    model = models[user.model]
    predicted_tokens = tokenize(messages)

    logger.debug(f"History construct done!")

    # 检查上下文长度是否足够
    if predicted_tokens > (model.context_length or float("inf")):
        await LLMMatcher.finish(
            f"\n上下文长度 {predicted_tokens} tokens 超过模型能够处理的最长长度 {model.context_length} tokens",
            at_sender=True,
        )
    
    logger.debug(f"Context length check done!")

    # 搜索记忆
    if config.ai.memory:
        from .memory import get_memprompt

        system_prompt.prompt += "\n" + await get_memprompt(session_id, prompt)
    
        logger.debug(f"Memory search done!")

    # 流式回复track
    reply_id = event.message_id
    msgs = []
    para_no = 1

    try:
        async for paragraph in chat(
            user.model,
            system_prompt.prompt,
            messages,
            system_prompt.temperature,
            system_prompt.frequency_penalty,
            system_prompt.presence_penalty,
            system_prompt.max_tokens,
        ):
            logger.debug(f"Sending paragraph {para_no} with reply_id {reply_id}.")
            data = await LLMMatcher.send(MessageSegment.reply(reply_id) + paragraph[0])
            reply_id = data["message_id"]
            msgs = paragraph[1]
            para_no += 1
        
        logger.debug(f"Reply done!")

        if config.ai.memory:
            from .memory import add_memory

            await add_memory(session_id, msgs[1:])
            logger.debug(f"Memory done!")

        logger.debug(dumps(msgs, ensure_ascii=False, indent=2))

        await LLMMatcher.finish()

    except HTTPError as e:
        await LLMMatcher.finish(MessageSegment.reply(reply_id) + f"上游异常：{e}")

    await LLMMatcher.finish(MessageSegment.reply(reply_id) + f"内部异常。")


# 设置系统提示词匹配器
prompt_cmd = Alconna("设置系统提示词", Args["prompt_name?", str])
PromptMatcher = on_alconna(prompt_cmd, block=True)


@PromptMatcher.handle()
async def set_prompt(
    user: Annotated[User, require()],
    prompt_name: Match[str],
):
    "设置系统提示词"

    if not prompt_name.available:
        await PromptMatcher.finish(
            "\n用法：设置系统提示词 <智能体名称>\n"
            "可用值：DEFAULT, UNSAFE 或已创建的智能体名称",
            at_sender=True,
        )

    agent = await Agent.get(prompt_name.result)

    if not (prompt_name.result in ["DEFAULT", "UNSAFE"] or agent):
        await PromptMatcher.finish("\n智能体不存在。", at_sender=True)

    await user.set({User.system_prompt: prompt_name.result})
    await PromptMatcher.finish("\n已尝试更新您的专属系统提示词", at_sender=True)


# 更换模型匹配器
model_cmd = Alconna("更改模型", Args["model_id?", str])
ModelChangeMatcher = on_alconna(model_cmd, block=True)


@ModelChangeMatcher.handle()
async def model_change(user: Annotated[User, require()], model_id: Match[str]):
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
            )
            + "\n\n注：消耗计算方式：接口给出的消耗Token数/1000*倍率，消耗积分。",
            at_sender=True,
        )
    await user.set({User.model: model_id.result})
    await ModelChangeMatcher.finish("\n成功为您更换模型。", at_sender=True)


SessionMatcher = on_alconna(Alconna("会话信息"), block=True)


@SessionMatcher.handle()
async def session_info(
    event: MessageEvent,
):
    "查看会话信息"

    session_id = get_session_id(event)
    vip = await get_vip(session_id)
    await SessionMatcher.finish(
        f"\n会话 ID：{session_id}\n"
        f"VIP 到期：{vip[1].strftime('%Y-%m-%d') if vip[1] and vip[1] > date.today() else '未开通'}",
        at_sender=True,
    )


ClearMemoryMatcher = on_alconna(Alconna("清除记忆"), block=True)


@ClearMemoryMatcher.handle()
async def clear_memory(
    event: MessageEvent,
):
    "清除记忆"

    if not config.ai or not config.ai.memory:
        await ClearMemoryMatcher.finish("\n记忆系统未启用。", at_sender=True)

    session_id = get_session_id(event)

    if session_id[0] == "g" and event.get_user_id() not in config.supermgr_ids:
        await ClearMemoryMatcher.finish(
            "\n只有超级管理员可以清除群聊会话的记忆。", at_sender=True
        )

    from .memory import clear_memory

    await clear_memory(session_id)
    await ClearMemoryMatcher.finish("\n已尝试清除本会话的记忆", at_sender=True)


GetMemoryMatcher = on_alconna(Alconna("查看记忆"), block=True)


@GetMemoryMatcher.handle()
async def get_memory(
    event: MessageEvent,
):
    "查看记忆"

    if not config.ai or not config.ai.memory:
        await GetMemoryMatcher.finish("\n记忆系统未启用。", at_sender=True)

    session_id = get_session_id(event)

    if session_id[0] == "g" and event.get_user_id() not in config.supermgr_ids:
        await GetMemoryMatcher.finish(
            "\n只有超级管理员可以查看群聊会话的记忆。", at_sender=True
        )

    from .memory import getall_memory

    memlist = await getall_memory(session_id)
    memstr = "\n".join(memlist)

    await GetMemoryMatcher.finish(f"\n当前所有记忆：\n{memstr}", at_sender=True)


# 添加智能体匹配器
add_agent_cmd = Alconna(
    "添加智能体",
    Args["agent_name?", str]["prompt?", str],
    Option("--temperature|-t", Args["temperature", float], help_text="温度参数"),
    Option(
        "--frequency_penalty|-f", Args["frequency_penalty", float], help_text="频率惩罚"
    ),
    Option(
        "--presence_penalty|-p", Args["presence_penalty", float], help_text="存在惩罚"
    ),
    Option("--max_tokens|-m", Args["max_tokens", int], help_text="最大输出长度"),
)
AddAgentMatcher = on_alconna(add_agent_cmd, block=True)


@AddAgentMatcher.handle()
async def add_agent(
    agent_name: Match[str],
    prompt: Match[str],
    arp: Arparma[Any],
):
    "添加智能体"

    if not agent_name.available or not prompt.available:
        await AddAgentMatcher.finish(
            "\n用法：添加智能体 <名称> <提示词> [选项]\n"
            "选项：\n"
            "  -t/--temperature <值>        温度参数 (默认1.0)\n"
            "  -f/--frequency_penalty <值>   频率惩罚 (默认0.0)\n"
            "  -p/--presence_penalty <值>    存在惩罚 (默认0.0)\n"
            "  -m/--max_tokens <值>          最大输出长度",
            at_sender=True,
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await AddAgentMatcher.finish("\n不允许使用保留名称。", at_sender=True)

    existing = await Agent.get(agent_name.result)
    if existing:
        await AddAgentMatcher.finish("\n该智能体已存在。", at_sender=True)

    agent = Agent(id=agent_name.result, prompt=prompt.result)
    if (t := arp.query[float]("temperature.temperature")) is not None:
        agent.temperature = t
    if (f := arp.query[float]("frequency_penalty.frequency_penalty")) is not None:
        agent.frequency_penalty = f
    if (p := arp.query[float]("presence_penalty.presence_penalty")) is not None:
        agent.presence_penalty = p
    if (m := arp.query[int]("max_tokens.max_tokens")) is not None:
        agent.max_tokens = m
    await agent.insert()
    await AddAgentMatcher.finish(
        f"\n已成功添加智能体 {agent_name.result}",
        at_sender=True,
    )


# 删除智能体匹配器
del_agent_cmd = Alconna("删除智能体", Args["agent_name?", str])
DelAgentMatcher = on_alconna(del_agent_cmd, block=True)


@DelAgentMatcher.handle()
async def del_agent(
    user: Annotated[User, require(superuser=True)],
    agent_name: Match[str],
):
    "删除智能体"

    if not agent_name.available:
        await DelAgentMatcher.finish(
            "\n用法：删除智能体 <名称>",
            at_sender=True,
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await DelAgentMatcher.finish("\n不允许删除保留智能体。", at_sender=True)

    agent = await Agent.get(agent_name.result)
    if not agent:
        await DelAgentMatcher.finish("\n该智能体不存在。", at_sender=True)

    await agent.delete()
    await DelAgentMatcher.finish(
        f"\n已成功删除智能体 {agent_name.result}",
        at_sender=True,
    )


# 修改智能体匹配器
edit_agent_cmd = Alconna(
    "修改智能体",
    Args["agent_name?", str],
    Option("--prompt", Args["prompt", str], help_text="提示词"),
    Option("--temperature|-t", Args["temperature", float], help_text="温度参数"),
    Option(
        "--frequency_penalty|-f", Args["frequency_penalty", float], help_text="频率惩罚"
    ),
    Option(
        "--presence_penalty|-p", Args["presence_penalty", float], help_text="存在惩罚"
    ),
    Option("--max_tokens|-m", Args["max_tokens", int], help_text="最大输出长度"),
)
EditAgentMatcher = on_alconna(edit_agent_cmd, block=True)


@EditAgentMatcher.handle()
async def edit_agent(
    user: Annotated[User, require(superuser=True)],
    agent_name: Match[str],
    arp: Arparma[Any],
):
    "修改智能体"

    if not agent_name.available:
        await EditAgentMatcher.finish(
            "\n用法：修改智能体 <名称> [选项]\n"
            "选项：\n"
            "  --prompt <提示词>             修改提示词\n"
            "  -t/--temperature <值>        温度参数\n"
            "  -f/--frequency_penalty <值>   频率惩罚\n"
            "  -p/--presence_penalty <值>    存在惩罚\n"
            "  -m/--max_tokens <值>          最大输出长度",
            at_sender=True,
        )

    if agent_name.result in ["DEFAULT", "UNSAFE"]:
        await EditAgentMatcher.finish("\n不允许修改保留智能体。", at_sender=True)

    agent = await Agent.get(agent_name.result)
    if not agent:
        await EditAgentMatcher.finish("\n该智能体不存在。", at_sender=True)

    updates: dict[str, str | float | int] = {}
    if (pr := arp.query[str]("prompt.prompt")) is not None:
        updates["prompt"] = pr
    if (t := arp.query[float]("temperature.temperature")) is not None:
        updates["temperature"] = t
    if (f := arp.query[float]("frequency_penalty.frequency_penalty")) is not None:
        updates["frequency_penalty"] = f
    if (p := arp.query[float]("presence_penalty.presence_penalty")) is not None:
        updates["presence_penalty"] = p
    if (m := arp.query[int]("max_tokens.max_tokens")) is not None:
        updates["max_tokens"] = m

    if not updates:
        await EditAgentMatcher.finish("\n请至少指定一个要修改的选项。", at_sender=True)

    await agent.set(updates)
    await EditAgentMatcher.finish(
        f"\n已成功修改智能体 {agent_name.result}，"
        f"更新了：{', '.join(updates.keys())}",
        at_sender=True,
    )
