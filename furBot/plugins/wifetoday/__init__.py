from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="WifeToday",
    description="自动选择一位群友作为今日老婆 —— 萝卜机器人开源实现",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

