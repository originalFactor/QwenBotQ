from nonebot import on_message, on_command
from nonebot.rule import to_me, startswith
from nonebot.adapters import Message
from nonebot.params import CommandArg, EventMessage
import dashscope
from http import HTTPStatus
from random import randint
from . import config
from typing import Union
from os.path import exists

# Initialize Dashscope Api Key
dashscope.api_key = config.dashscope_api_key

# [PRIVATE] Message Handler
autoReply = on_message(rule=to_me()&startswith("/askGPT"))
@autoReply.handle()
async def autoReplyHandler(message:Message = EventMessage()):
    if userRequest := message.extract_plain_text():
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
            await autoReply.finish(response.output.choices[0].message.content) # type: ignore
        await autoReply.finish("不知道通义服务器炸了还是我代码炸了")
    await autoReply.finish("没问题怎么问呢？")

# Initialize System Prompt
def applyPrompt(prompt:Union[str,None]=None, nick:Union[str,None]=None):
    global SYSTEM_PROMPT, CHATBOT_NICKNAME, autoReply
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
    else: CHATBOT_NICKNAME = "GPT"
    autoReply.rule = to_me()&startswith(CHATBOT_NICKNAME)
applyPrompt()

# [PRIVATE] `/profile` Handler
profile = on_command('profile',to_me())
@profile.handle()
async def profileHandler(args:Message = CommandArg()):
    txtArgs = args.extract_plain_text().split()
    applyPrompt(*((' '.join(txtArgs[:-1]), txtArgs[-1]) if txtArgs else ()))
    await profile.finish("已应用配置！")

