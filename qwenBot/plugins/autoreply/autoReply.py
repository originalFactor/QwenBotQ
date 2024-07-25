# Nonebot
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot.params import CommandArg
# Qwen
import dashscope
from http import HTTPStatus
# Random
from random import randint
# self
from . import config

# Initialize Dashscope Api Key
dashscope.api_key = config.dashscope_api_key

# [PRIVATE] `/autoReply` handle
autoReply = on_command('autoReply',to_me())
@autoReply.handle()
async def autoReplyHandler(args:Message=CommandArg()):
    if userRequest := args.extract_plain_text():
        response = dashscope.Generation.call(
            model="qwen-max-longcontext",
            messages=[
                {'role': 'system', 'content': config.system_prompt}, # type: ignore
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

