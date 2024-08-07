from nonebot import on_command
from nonebot.rule import to_me
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent
from asyncio import sleep
from .database import isFirstTime
from . import config

# [TO ME] `/init`
init = on_command('init',to_me(),permission=SUPERUSER)
@init.handle()
async def checkInit(event:GroupMessageEvent):
    await isFirstTime()
    await init.finish(MessageSegment.at(event.user_id)+'\n已尝试初始化数据库。')

# [TO ME] `/help`
help = on_command('help')
@help.handle()
async def helpMsg(event:GroupMessageEvent, bot:Bot):
    msg = (await help.send(
        MessageSegment.at(event.user_id)+
        '''
欢迎使用 AIO 机器人！
GitHub Repository: https://github.com/originalFactor/QwenBotQ/

方舟功能：
`方舟抽卡` 朴素的十连
`方舟十连` 华丽的十连
该功能由外部插件提供支持！

AI功能：
`/llm <msg>` 通义千问回复
`/prompt <msg>` 设置**全局**专属系统提示词，仅对你的消息有效

个人中心功能：
`/wife` 随机获取**本群**对象，当天**全局**互相绑定，不可更改
`/refresh` 消耗积分换对象
`/info [@someone]` 查看**全局**个人资料
`/sign` 每日签到获取积分

本群功能：
`/词云` 获取词云插件使用帮助(不受本系统控制)

全局功能：
`/rank` 获取**全局**积分排行榜

超管功能：
`/grant <@someone>` 赋予比自己权限等级小一级的**全局**权限。
`/bind <@A> <@B>` 强制绑定**全局**关系

调试功能：
第一次使用/升级后请发送配置文件中设定的重置数据库指令，重置后用户数据清空。
`/members` 获取**本群**成员列表

危险功能：
`/init` 初始化数据库 **该命令仅@bot且有初始超管权限才能使用**

温馨提醒：
请不要设置过长的系统提示，或在大群中获取群成员列表，可能会导致较长延迟并影响体验

（以上命令部分特殊值需要足够权限才能使用）
    '''))['message_id']

    await sleep(10)
    await bot.delete_msg(message_id=msg)
    await help.finish()
