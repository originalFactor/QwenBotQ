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

在开始之前，请确保您安装了 Python 3 版本 `>=3.9`。

否则，对于 Windows 系统，您可能需要 [在此处下载](https://www.python.org/downloads/windows/)。

对于 Linux，系统一般情况下已经自带了Python 3，否则您可以尝试：
```sh
# Debian/Ubuntu
sudo apt install python3

# RHEL/CentOS
sudo yum install python3

# ArchLinux
sudo pacman -Syu python3
```

若您系统自带的 Python 3 版本过低，请尝试 [pyenv](https://github.com/pyenv/pyenv#installation)

并且确保您安装了 Poetry 管理器。

如果您还没有安装 Poetry ，请在终端中执行如下代码：
```sh
pip install poetry
```

## 部署后端

欧！先别急！因为这只是一个客户端——它只实现了机器人本身的逻辑，而没有对接具体的平台。

这个项目使用 Nonebot2 框架，且为 NapCat 精心设计。

虽然从理论上来说，NapCat 应当兼容 OneBot V11 和 Go-CQHTTP 协议，但事实上并不是这样。

因此，该项目为 NapCat 进行了一些深度兼容，导致破坏了与其他服务端的兼容性——事实上仅有一个功能受影响。

群精华——`get_essence_msg_list`接口，NapCat 的返回格式与其他后端不同。我们为此专门做了兼容。

总而言之，你可以使用任何 OneBot V11 后端，但是无法使用群精华功能，除非您使用 NapCat。

具体的 NapCat 安装教程可以在 [这里](https://napcat.napneko.icu/guide/start-install) 看到。

然后你需要进行一些 [配置](https://napcat.napneko.icu/config/basic)，具体包括登录、启用正向WS服务。

其他的配置项正常情况下不需要改动。如果有问题，可以提 Issue。

## 开始工作！

首先，让我们拉取项目并展开工作目录
```sh
# 先拉取项目
git clone https://github.com/originalFactor/QwenBotQ.git
# 进入项目目录
cd QwenBotQ
```

然后编辑配置文件以使它符合我们的情况
```sh
# 将模板文件复制
cp example.env.prod .env.prod
# 编辑配置文件
vim .env.prod
```
[参考文档](reference.md)

尤其需要更改 `SUPERUSERS` 内数据为你的超管QQ号，
将 `ONEBOT_WS_URLS` 内数据改为 `ws://<NapCat所在服务器IP地址或域名>:3001`，
更改 `MONGO_URI` 为你的数据库地址，
`API_KEY` 为你的阿里云灵积API-KEY。

接下来，我们安装依赖
```sh
poetry install
```

然后就可以运行机器人了
```sh
python ./bot.py
```
