# Copyright (C) 2024 originalFactor
#
# This file is part of QwenBotQ.
#
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

"The global initialize module of QwenBotQ."

from nonebot import on_command
from .bot_utils import strict_to_me
from nonebot.permission import SUPERUSER

BOOK = '''
欢迎使用机的万能机器人~
GitHub: https://github.com/originalFactor/QwenBotQ
项目相关请使用GitHub Discussions讨论

功能列表：
- 说明书
  查看本条信息
- @机器人 你的问题
  调用大模型回答你的问题~
- 设置系统提示词 提示词
  设置可以用来调教的系统提示词~只对你的信息有效
- 用户信息 [@用户]
  查看用户信息
- 授予权限 @用户
  授予用户比自己低一级的管理员权限，需要自身有2级以上权限
- 官宣 @用户 @用户
  既然你们两个都是公认的CP了，那就永远绑在一起吧（雾）
- 今日老公
  召唤你的群友老公
- 群友列表
  看看机器人能读到哪些群友（人多的群会造成严重延迟以及刷屏）
- 签到
  每日签到，可以获得随机积分奖励~
- 积分榜
  查看积分前十
- 换老公
  对老公不满意？花点积分换一个！
- 印钞机
  什么？你是管理？印点钱花又不会怎么样
- 转账给 @用户 数量
  转账给指定用户指定数量的积分，可以用来交易~本来1积分就相当于1毛钱来的
- 恢复记录
  之前抽到了稀有老公但没有及时续费？没事，引用当时的回复并花点积分就行！
- 续期
  续费你的老公，防止他过期
- 更改模型 [模型]
  更改大模型，不提供参数则获取模型列表

注：[参数]代表可选参数， @用户 可用 @用户QQ号 代替。
'''

# 指南
HelpMatcher = on_command('说明书', block=True)


@HelpMatcher.handle()
async def help_message():
    '`说明书`命令handler'
    await HelpMatcher.finish(
        '\n'+BOOK.strip(),
        at_sender=True
    )
