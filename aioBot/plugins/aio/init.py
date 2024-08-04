from nonebot import on_command
from nonebot.rule import to_me
from .database import isFirstTime

# [TO ME] `/init`
init = on_command('init',to_me())
@init.handle()
async def checkInit():
    await isFirstTime()
    await init.finish('已尝试初始化数据库。')

# [TO ME] `/help`
help = on_command('help',to_me())
@help.handle()
async def helpMsg():
    await help.finish(
        '''
欢迎使用 AIO 机器人！
GitHub Repository: https://github.com/originalFactor/QwenBotQ/

功能列表：
（注：以下功能均需@bot触发）
`/llm <msg>` 调用阿里云灵积平台通义千问大模型回复消息
`/setPrompt <msg>` 设置专属系统提示词，仅对你的消息有效
`/wife` 随机获取一名群员作为老公，当天互相绑定，不可更改
`/grantPermission` 超管引用对方消息，可赋予超管权限
`/bind <A> <B>` 强制绑定Couple，仅超管可用
`/getInformation` 查看个人资料
`/groupMembers` 查看群组成员

温馨提醒：


（以上命令部分特殊值需要足够权限才能使用）
''')
