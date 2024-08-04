from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="AIO",
    description="All things interesting to improve chatroom expierence.",
    usage="@bot /help",
    type="application",
    config=Config,
    homepage="https://github.com/originalFactor/QwenBotQ/"
)

config = get_plugin_config(Config)

from .autoReply import *
from .init import *