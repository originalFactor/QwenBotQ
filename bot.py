from sys import stdout
from os import environ
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter
from nonebot.log import logger_id, default_filter

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

nonebot.load_plugin("nonebot_plugin_wordcloud")
nonebot.load_plugin("nonebot_plugin_arkgacha")
nonebot.load_plugin("nonebot_plugin_memes")
nonebot.load_plugin("core")

if __name__ == "__main__":
    nonebot.run()
