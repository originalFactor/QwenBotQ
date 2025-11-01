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

## 准备工作

> 推荐使用 Python 3.11。其他版本可能出现意料外的兼容性问题。

在开始之前，请确保您安装了 Python 3 版本 `>=3.9`。

对于 Windows 系统，您可能需要 [在此处下载](https://www.python.org/downloads/windows/)。

若您系统自带的 Python 3 版本过低，请尝试 [pyenv](https://github.com/pyenv/pyenv#installation)

并且确保您安装了 [Poetry 管理器](https://python-poetry.org/docs/#installation)。

## 部署后端

欧！先别急！因为这只是一个客户端——它只实现了机器人本身的逻辑，而没有对接具体的平台。

这个项目使用 Nonebot2 框架，且为 NapCat 精心设计。

虽然从理论上来说，NapCat 应当兼容 OneBot V11 和 Go-CQHTTP 协议，但事实上并不是这样。

因此，该项目为 NapCat 进行了一些深度兼容，导致破坏了与其他服务端的兼容性——事实上仅有一个功能受影响。

群精华——`get_essence_msg_list`接口，NapCat 的返回格式与其他后端不同。我们为此专门做了兼容。

总而言之，你可以使用任何 OneBot V11 后端，但是无法使用群精华功能，除非您使用 NapCat。

具体的 NapCat 安装教程可以在 [这里](https://napcat.napneko.icu/guide/start-install) 看到。

然后你需要进行一些 [配置](https://napcat.napneko.icu/config/basic)，具体包括登录、启用正向 WS 服务。

其他的配置项正常情况下不需要改动。如果有问题，可以提 Issue。

## 拉取项目

```sh
# 先拉取项目
git clone https://github.com/originalFactor/QwenBotQ.git
# 进入项目目录
cd QwenBotQ
# 安装依赖
poetry install
```

## 安装数据库

运行本项目之前，您必须拥有一个 MongoDB 数据库。

您可以在 [MongoDB 官网](https://www.mongodb.com/) 下载并安装。

您也可以使用 [MongoDB Atlas](https://www.mongodb.com/atlas) 或者其他基于云的服务。

对于本机数据库，您无需添加额外的配置项。

对于 MongoDB Atlas，您需要在 `.env.prod` 中添加如下配置项：

```dotenv
MONGO_URI='您的 MongoDB 连接字符串'
MONGO_DB='您的数据库名称'
```

以上内容应由您的数据库提供方提供。

## 配置基础设置

您需要编辑一些基础的配置项：

```dotenv
# 固定
DRIVER=~aiohttp
COMMAND_START=[""]

# OneBot Token，在 NapCat 面板中设置，必须设置
ONEBOT_ACCESS_TOKEN=token

# OneBot WS 地址，在 NapCat 面板中设置，必须设置
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]

# 超级用户，拥有一些管理员指令的权限，可以不设置
SUPERUSERS=["12345678"]

# OpenAI format API 端点，默认为 OpenAI 官方端点
BASE_URL='https://api.deepseek.com/beta'

# 端点的 API Key，必须设置
API_KEY='sk-xxxx'

# AI 的系统提示词，默认为 'You are a smart assistant.'
SYSTEM_PROMPT='你是一个聊天机器人，你可以解答用户的问题，或者插科打诨，你使用QQ聊天，你应避免使用Markdown等QQ不支持的格式'

# 模型列表
MODELS='
{
    "deepseek-chat": {  # API 端点中的模型ID
        "name": "DeepSeek V3",  # 模型名称
        "input_cost": 0.2,  # 输入价格，积分/kTokens，向上取整
        "output_cost": 0.8,  # 输出价格，积分/kTokens，向上取整
        "max_tokens": 4096,  # 最大输出Tokens
        "context_length": 65536,  # 最大上下文长度
        "detail": "DeepSeek V3 最新模型"  # 模型介绍
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
