# Copyright (C) 2024 OriginalFactor
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

'机器人启动文件'

from sys import stdout, platform
from os import environ
import asyncio
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.log import logger_id, default_filter

# 修复 AIODNS 错误
if platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 作为服务运行时不重复输出时间
if environ.get('RUNNING_AS_SERVICE', 'no') == 'yes':
    nonebot.logger.remove(logger_id)
    nonebot.logger.add(
        stdout,
        level=0,
        diagnose=True,
        format="[<lvl>{level}</lvl>] <c><u>{name}</u></c> | {message}",
        filter=default_filter
    )

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OnebotV11Adapter)

nonebot.load_plugin("qwenbotq")

if __name__ == "__main__":
    nonebot.run()
