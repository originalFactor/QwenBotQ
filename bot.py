from sys import stdout
from os import environ
import nonebot
from nonebot.adapters.satori import Adapter as SatoriAdapter
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
driver.register_adapter(SatoriAdapter)

nonebot.load_plugin("nonebot_plugin_status")
nonebot.load_plugin("qwenbotq")

if __name__ == "__main__":
    nonebot.run()
