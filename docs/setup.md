<!--
 Copyright (C) 2024 originalFactor
 
 This file is part of QwenBotQ.
 
 QwenBotQ is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 QwenBotQ is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 
 You should have received a copy of the GNU General Public License
 along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.
-->

# 安装

** 本文仅包含运行本项目的信息，请自行设置OneBot v11后端 **

```sh
# 先拉取项目
git clone https://github.com/originalFactor/QwenBotQ.git
# 进入项目目录
cd QwenBotQ
# 按提示编辑配置文件
vim .env.prod.example
# 更改文件名
mv .env.prod.example .env.prod
# 安装Nonebot2以及插件
python3 -m pip install nonebot2 nonebot-adapter-onebot nonebot-plugin-arkgacha nonebot-plugin-wordcloud nonebot-plugin-memes
# 设置代理
export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897
# 初始化方舟
arkkit init -SIMG
# 运行机器人
python3 ./bot.py
```
