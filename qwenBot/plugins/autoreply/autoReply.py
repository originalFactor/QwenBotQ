from nonebot import on_message, on_command
from nonebot.rule import to_me, startswith
from nonebot.adapters import Message
from nonebot.params import CommandArg, EventMessage
from nonebot import logger
import dashscope
from http import HTTPStatus
from random import randint
from . import config
from typing import Union
from os.path import exists

# Initialize Dashscope Api Key
dashscope.api_key = config.dashscope_api_key

# [PRIVATE] Message Handler
autoReply = on_message(rule=to_me())
@autoReply.handle()
async def autoReplyHandler(message:Message = EventMessage()):
    userRequest = message.extract_plain_text()
    if userRequest and CHATBOT_NICKNAME in userRequest:
        response = dashscope.Generation.call(
            model="qwen-max-longcontext",
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT}, # type: ignore
                {'role': 'user', 'content': userRequest}
            ],
            seed=randint(1,10000),
            temprature=0.8,
            top_p=0.8,
            top_k=50,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK: # type: ignore
            await autoReply.finish('[Github.com/originalFactor/QwenBotQ] 回复：'+response.output.choices[0].message.content) # type: ignore
        await autoReply.finish(f"[Github.com/originalFactor/QwenBotQ] 错误：API服务器返回状态码{response.status_code}") # type: ignore
    await autoReply.finish()

# Initialize System Prompt
def applyPrompt(prompt:Union[str,None]=None, nick:Union[str,None]=None):
    global SYSTEM_PROMPT, CHATBOT_NICKNAME
    if prompt:
        with open("SYSTEM_PROMPT.txt",'w') as f:
            f.write(prompt)
        SYSTEM_PROMPT = prompt
    elif exists("SYSTEM_PROMPT.txt"):
        with open("SYSTEM_PROMPT.txt",'r') as f:
            SYSTEM_PROMPT = f.read()
        return
    else: SYSTEM_PROMPT = "You are a helpful assistant."
    if nick:
        with open("CHATBOT_NICKNAME.txt",'w') as f:
            f.write(nick)
        CHATBOT_NICKNAME = nick
    elif exists("CHATBOT_NICKNAME.txt"):
        with open("CHATBOT_NICKNAME.txt",'r') as f:
            CHATBOT_NICKNAME = f.read()
    else: CHATBOT_NICKNAME = "/askGPT"
applyPrompt()

# [PRIVATE] `/profile` Handler
profile = on_command('profile',to_me())
@profile.handle()
async def profileHandler(args:Message = CommandArg()):
    txtArgs = args.extract_plain_text().split()
    prompt, nick = ' '.join(txtArgs[:-1]), txtArgs[-1]
    applyPrompt(prompt, nick)
    await profile.finish("[Github.com/originalFactor/QwenBotQ] 提示：已应用配置！"
        f"系统提示词：{prompt if prompt else '未更改'},"
        f"召唤关键词：{nick if nick else '未更改'}"
    )
