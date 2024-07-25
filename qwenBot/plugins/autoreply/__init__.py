from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="autoReply",
    description="Automatic reply powered by Qwen LLM.",
    usage="@bot /autoReply <message>",
    config=Config,
    type="application",
    homepage="https://github.com/originalFactor/QwenBotQ/"
)

config = get_plugin_config(Config)

from .autoReply import *