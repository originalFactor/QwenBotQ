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

'QwenBotQ 主要部分'

from importlib import import_module
from nonebot import get_plugin_config, require
from nonebot.plugin import PluginMetadata
from .config_model import Config

__plugin_meta__ = PluginMetadata(
    name="QwenBotQ",
    description="杂七杂八的花里胡哨功能",
    usage="@bot /help",
    type="application",
    config=Config,
    homepage="https://github.com/originalFactor/QwenBotQ/",
    supported_adapters={"nonebot-adapter-onebot"}
)

config = get_plugin_config(Config)

# 声明依赖
require("nonebot_plugin_apscheduler")

# 导入功能模块
import_module(".usersystem", __package__)
import_module(".ai", __package__)
import_module(".binding", __package__)
import_module(".group", __package__)
import_module(".bilinotice", __package__)

# 因为auotopep8和pylint都要求在代码之前导入，但是这样就获取不到正确的config对象，所以我只能另辟蹊径了XwX
