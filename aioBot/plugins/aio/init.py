from nonebot import on_command
from .database import isFirstTime
from . import config

# [TO ME] `/init`
init = on_command(config.system_reset_command)
@init.handle()
async def checkInit():
    await isFirstTime()
    await init.finish('已尝试初始化数据库。')

# [TO ME] `/help`
help = on_command('help')
@help.handle()
async def helpMsg():
    await help.finish(
        '''欢迎使用 AIO 机器人！
GitHub Repository: https://github.com/originalFactor/QwenBotQ/

功能列表：
`/llm <msg>` 通义千问回复
`/prompt <msg>` 设置**全局**专属系统提示词，仅对你的消息有效
`/wife` 随机获取**本群**对象，当天**全局**互相绑定，不可更改
`/info [@someone]` 查看**全局**个人资料

超管功能：
`/grant <@someone>` 赋予比自己权限等级小一级的**全局**权限。
`/bind <@A> <@B>` 强制绑定**全局**关系

调试功能：
第一次使用/升级后请发送配置文件中设定的重置数据库指令，重置后用户数据清空。
`/members` 获取**本群**成员列表

拓展功能：
`/sign` 每日签到
`/rank` 获取**全局**排行榜
`/refresh` 消耗积分换对象

温馨提醒：
请不要设置过长的系统提示，或在大群中获取群成员列表，可能会导致较长延迟并影响体验

（以上命令部分特殊值需要足够权限才能使用）
''')
