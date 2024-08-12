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

from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="AIO",
    description="All things interesting to improve chatroom expierence.",
    usage="@bot /help",
    type="application",
    config=Config,
    homepage="https://github.com/originalFactor/QwenBotQ/",
    supported_adapters={"nonebot-adapter-onebot"}
)

config = get_plugin_config(Config)

from .bot import *
from .init import *