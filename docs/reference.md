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

# 环境变量配置参考

> 注意：环境变量的名称不区分大小写。

## Nonebot2 框架基础配置

如需查看完整配置列表，请访问 [官方文档](https://nonebot.dev/docs/appendices/config#%e5%86%85%e7%bd%ae%e9%85%8d%e7%bd%ae%e9%a1%b9)。

| 配置项                 | 数据类型   | 默认值      | 说明                                            |
| ---------------------- | ---------- | ----------- | ----------------------------------------------- |
| driver                 | 字符串     | `~fastapi`  | 驱动类型，本项目使用 `~aiohttp`                 |
| host                   | IP 地址    | `127.0.0.1` | 机器人监听的主机地址                            |
| port                   | 整数       | `8080`      | 机器人监听的端口号                              |
| log_level              | 字符串     | `info`      | 日志输出级别                                    |
| api_timeout            | 浮点数     | `30.0`      | 平台接口调用的超时时间（秒）                    |
| superusers             | 字符串集合 | `[]`        | 超级用户列表，初始权限等级为 3                  |
| nickname               | 字符串集合 | `[]`        | 机器人昵称，会自动获取                          |
| command_start          | 字符串集合 | `["/"]`     | 命令起始符号，本项目使用 `[""]`（即不需要前缀） |
| command_sep            | 字符串集合 | `["."]`     | 命令分隔符号                                    |
| session_expire_timeout | 时间间隔   | `00:02:00`  | 用户会话的超时时间                              |

## OneBot V11 适配器配置

如需查看完整配置列表，请访问 [官方文档](https://onebot.adapters.nonebot.dev/docs/api/v11/config)。

| 配置项              | 数据类型           | 默认值 | 说明                          |
| ------------------- | ------------------ | ------ | ----------------------------- |
| onebot_access_token | 字符串             | `空`   | 连接认证的令牌                |
| onebot_secret       | 字符串             | `空`   | 上报数据的签名密钥            |
| onebot_ws_urls      | WebSocket URL 集合 | `[]`   | 正向 WebSocket 连接的目标地址 |

## QwenBotQ 特有配置

| 配置项               | 数据类型         | 默认值                         | 说明                                                                     |
| -------------------- | ---------------- | ------------------------------ | ------------------------------------------------------------------------ |
| mongo_uri            | 字符串           | `mongodb://127.0.0.1:27017`    | MongoDB 数据库连接地址                                                   |
| mongo_db             | 字符串           | `aioBot`                       | 用于数据存储的数据库名称（如果在同一服务器运行多个实例，需设置不同名称） |
| api_key              | 字符串           | 必填项                         | 阿里云灵积（百炼）平台的 API 密钥                                        |
| system_prompt        | 字符串           | `You are a smart assistant.`   | 新用户默认使用的系统提示词                                               |
| models               | 模型配置映射     | 参见下方                       | 可用的 AI 模型列表                                                       |
| set_prompt_cost      | 整数             | `1`                            | 设置系统提示词所需的积分                                                 |
| daily_sign_max_coins | 整数             | `50`                           | 每日签到可获得的最大积分                                                 |
| daily_sign_min_coins | 整数             | `1`                            | 每日签到可获得的最小积分                                                 |
| refresh_price        | 整数             | `1`                            | 解除绑定所需的积分                                                       |
| fork_cost            | 整数             | `1`                            | 从可信来源恢复数据所需的积分                                             |
| renew_cost           | 整数             | `1`                            | 续期绑定所需的积分                                                       |
| trusted_wife_source  | QQ 号列表        | `["3003535850", "1297825911"]` | 可信来源的 QQ 号列表                                                     |
| grant_cost           | 整数             | `1`                            | 超级管理员授权小管理员所需的积分                                         |
| bind_cost            | 整数             | `1`                            | 指定绑定所需的积分                                                       |
| charge_min_perm      | 整数             | `1`                            | 使用印钞机功能所需的最小权限等级                                         |
| focus                | 哔哩哔哩推送配置 | `None`                         | B 站动态推送功能的设置                                                   |

### 模型配置示例

`models` 字段的默认配置如下：

```json
{
  "qwen-max": {
    "name": "通义千问-max",
    "input_cost": 2,
    "output_cost": 6,
    "max_tokens": 30720,
    "detail": "通义千问系列效果最好的模型，适合复杂、多步骤的任务。"
  },
  "qwen-plus": {
    "name": "通义千问-plus",
    "input_cost": 0.08,
    "output_cost": 0.02,
    "max_tokens": 129024,
    "detail": "能力均衡，推理效果、成本和速度介于通义千问-max和通义千问-turbo之间，适合中等复杂任务。"
  },
  "qwen-turbo": {
    "name": "通义千问-turbo",
    "input_cost": 0.03,
    "output_cost": 0.06,
    "max_tokens": 129024,
    "detail": "通义千问系列速度最快、成本很低的模型，适合简单任务。"
  },
  "qwen-long": {
    "name": "通义千问-long",
    "input_cost": 0.05,
    "output_cost": 0.2,
    "max_tokens": 10000000,
    "detail": "支持总结和分析长达千万字的文档，且成本极低。"
  }
}
```

### Model 对象结构说明

| 字段名      | 数据类型 | 默认值    | 说明                     |
| ----------- | -------- | --------- | ------------------------ |
| name        | 字符串   | `Unknown` | 模型的易读名称           |
| input_cost  | 浮点数   | `0.0`     | 输入内容的积分消耗倍率   |
| output_cost | 浮点数   | `0.0`     | 输出内容的积分消耗倍率   |
| max_tokens  | 可选整数 | `None`    | 模型支持的最大上下文长度 |
| detail      | 字符串   | `空`      | 模型的详细介绍说明       |

### FocusOptions 对象结构说明

| 字段名     | 数据类型     | 默认值         | 说明                                                                         |
| ---------- | ------------ | -------------- | ---------------------------------------------------------------------------- |
| sessdata   | 字符串       | 必填项         | 哔哩哔哩 Cookie 中 SESSDATA 的值，用于 API 调用验证                          |
| subscribes | 推送配置列表 | 必填项         | B 站动态推送的具体配置列表                                                   |
| interval   | 时间间隔映射 | `{"hours": 1}` | 检查更新的时间间隔，可用单位：`weeks`、`days`、`hours`、`minutes`、`seconds` |

### Focus 对象结构说明

| 字段名 | 数据类型  | 默认值 | 说明                       |
| ------ | --------- | ------ | -------------------------- |
| uid    | 字符串    | 必填项 | UP 主的 UID                |
| groups | 群号列表  | `[]`   | 需要推送动态的 QQ 群列表   |
| users  | QQ 号列表 | `[]`   | 需要推送动态的 QQ 用户列表 |
