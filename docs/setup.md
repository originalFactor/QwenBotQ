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

# 安装指南

## 准备环境

> 推荐使用 Python 3.11 版本，其他版本可能存在兼容性问题。

在开始安装前，请确保您的系统已安装 Python 3.9 或更高版本：

- Windows 用户可通过 [Python 官网](https://www.python.org/downloads/windows/) 下载安装
- 如果系统自带的 Python 版本较低，建议使用 [pyenv](https://github.com/pyenv/pyenv#installation) 管理多版本 Python

另外，还需要安装 [Poetry 包管理器](https://python-poetry.org/docs/#installation)。

## 部署后端服务

请注意：这只是一个机器人客户端程序，它只实现了机器人的核心逻辑，需要配合后端服务才能运行。

本项目基于 Nonebot2 框架开发，并特别针对 NapCat 进行了优化适配。虽然理论上 NapCat 兼容 OneBot V11 和 Go-CQHTTP 协议，但实际使用中存在差异。

目前只有一个功能受兼容性影响：群精华功能。这是因为 NapCat 的 `get_essence_msg_list` 接口返回格式与其他后端不同，我们为此做了专门适配。

简单来说：您可以使用任何 OneBot V11 后端，但只有使用 NapCat 时才能正常使用群精华功能。

您可以参考 [NapCat 官方安装指南](https://napcat.napneko.icu/guide/start-install) 完成安装，并按 [配置教程](https://napcat.napneko.icu/config/basic) 完成基础设置（主要是登录账号和启用正向 WebSocket 服务）。

其他配置项保持默认即可，如有问题欢迎提交 Issue。

## 获取项目代码

```sh
# 克隆项目代码
git clone https://github.com/originalFactor/QwenBotQ.git
# 进入项目目录
cd QwenBotQ
# 安装项目依赖
poetry install
```

## 安装和配置数据库

运行本项目前，您需要准备一个 MongoDB 数据库：

- 您可以在 [MongoDB 官网](https://www.mongodb.com/) 下载并本地安装
- 也可以使用 [MongoDB Atlas](https://www.mongodb.com/atlas) 或其他云数据库服务

如果使用本地数据库，无需额外配置；如果使用 MongoDB Atlas 等云服务，需要在 `.env.prod` 文件中添加如下配置：

```dotenv
MONGO_URI='您的 MongoDB 连接字符串'
MONGO_DB='您的数据库名称'
```

这些信息通常由您的数据库服务提供方提供。

## 基础配置说明

您需要在配置文件中设置以下基础参数：

```dotenv
# 固定配置项，无需修改
DRIVER=~aiohttp
COMMAND_START=[""]

# OneBot Token，必须设置，可在 NapCat 面板中配置
ONEBOT_ACCESS_TOKEN=token

# OneBot WebSocket 地址，必须设置，可在 NapCat 面板中查看
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]

# 超级用户账号列表，拥有管理员权限，可选配置
SUPERUSERS=["12345678"]

# OpenAI 格式 API 端点，默认为 OpenAI 官方端点
BASE_URL='https://api.deepseek.com/beta'

# API 密钥，必须设置
API_KEY='sk-xxxx'

# AI 系统提示词，默认值为 'You are a smart assistant.'
SYSTEM_PROMPT='你是一个聊天机器人，你可以解答用户的问题，或者插科打诨，你使用QQ聊天，你应避免使用Markdown等QQ不支持的格式'

# 模型配置列表
MODELS='
{
    "deepseek-chat": {  # API 中使用的模型ID
        "name": "DeepSeek V3",  # 显示给用户的模型名称
        "input_cost": 0.2,  # 输入价格，单位：积分/kTokens（向上取整）
        "output_cost": 0.8,  # 输出价格，单位：积分/kTokens（向上取整）
        "max_tokens": 4096,  # 最大输出Tokens数量
        "context_length": 65536,  # 模型最大上下文长度
        "detail": "DeepSeek V3 最新模型"  # 模型详细介绍
    }
}
```

更详细的配置项参考 [这个文档](reference.md)

也可以直接查看代码 [config_model.py](https://github.com/originalFactor/QwenBotQ/blob/dev/qwenbotq/config_model.py)

## 启动项目

```sh
# 启动项目
poetry run nb run
```
