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

# 环境变量参考

注：环境变量不分大小写。

## Nonebot2 配置

[完全列表](https://nonebot.dev/docs/appendices/config#%e5%86%85%e7%bd%ae%e9%85%8d%e7%bd%ae%e9%a1%b9)

| 键                     | 类型          | 默认值      | 解释                         |
| ---------------------- | ------------- | ----------- | ---------------------------- |
| driver                 | str           | `~fastapi`  | 驱动器，本项目使用`~aiohttp` |
| host                   | IPvAnyAddress | `127.0.0.1` | 监听的主机名                 |
| port                   | int           | `8080`      | 监听的端口                   |
| log_level              | str           | `info`      | 日志输出等级                 |
| api_timeout            | float         | `30.0`      | 平台接口调用超时时间         |
| superusers             | Set[str]      | `[]`        | 超管，初始权限为3            |
| nickname               | Set[str]      | `[]`        | 机器人昵称，自动获取         |
| command_start          | Set[str]      | `["/"]`     | 命令起始符，本项目使用`[""]` |
| command_sep            | Set[str]      | `["."]`     | 命令分隔符                   |
| session_expire_timeout | timedelta     | `00:02:00`  | 用户会话超时时间             |

## OneBot V11 适配器配置

[完全列表](https://onebot.adapters.nonebot.dev/docs/api/v11/config)

| 键                  | 类型       | 默认值 | 解释             |
| ------------------- | ---------- | ------ | ---------------- |
| onebot_access_token | str        | ``     | 授权令牌         |
| onebot_secret       | str        | ``     | 上报数据签名口令 |
| onebot_ws_urls      | Set[WSUrl] | `[]`   | 正向ws目标url    |

## QwenBotQ 配置

| 键                   | 类型                   | 默认值                         | 解释                                                 |
| -------------------- | ---------------------- | ------------------------------ | ---------------------------------------------------- |
| mongo_uri            | str                    | `mongodb://127.0.0.1:27017`    | MongoDB 数据库地址                                   |
| mongo_db             | str                    | `aioBot`                       | 用于存储的数据库名（如果要在同一服务器存储多个实例） |
| api_key              | str                    | 必填                           | 阿里云灵积（百炼）API-Key                            |
| system_prompt        | str                    | `You are a smart assistant.`   | 新用户的默认系统提示词                               |
| models               | Mapping[str, Model]    | 参见下方                       | 可用模型列表                                         |
| set_prompt_cost      | int                    | `1`                            | 设置系统提示词需要的积分数                           |
| daily_sign_max_coins | int                    | `50`                           | 每日签到获得最大积分数                               |
| daily_sign_min_coins | int                    | `1`                            | 每日签到获得最小积分数                               |
| refresh_price        | int                    | `1`                            | 解除绑定所需积分数                                   |
| fork_cost            | int                    | `1`                            | 从可信来源恢复数据所需积分数                         |
| renew_cost           | int                    | `1`                            | 续期绑定所需积分数                                   |
| trusted_wife_source  | Sequence[str]          | `["3003535850", "1297825911"]` | 可信来源QQ号列表                                     |
| grant_cost           | int                    | `1`                            | 超管授权小管理所需积分数                             |
| bind_cost            | int                    | `1`                            | 指定绑定所需积分数                                   |
| charge_min_perm      | int                    | `1`                            | 印钞机所需最小权限                                   |
| focus                | Optional[FocusOptions] | `None`                         | 哔哩哔哩推送设置                                     |

`models` 字段的默认值如下
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

### Model 对象

| 键          | 类型          | 默认值    | 解释           |
| ----------- | ------------- | --------- | -------------- |
| name        | str           | `Unknown` | 模型易读名称   |
| input_cost  | float         | `0.0`     | 输入消耗倍率   |
| output_cost | float         | `0.0`     | 输出消耗倍率   |
| max_tokens  | Optional[int] | `None`    | 最大上下文长度 |
| detail      | str           | ``        | 介绍           |

### FocusOptions 对象

| 键         | 类型              | 默认值         | 解释                                                                     |
| ---------- | ----------------- | -------------- | ------------------------------------------------------------------------ |
| sessdata   | str               | 必填           | 哔哩哔哩Cookie里SESSDATA项的值，用于调用API时的验证                      |
| subscribes | Sequence[Focus]   | 必填           | 推送配置列表                                                             |
| interval   | Mapping[str, int] | `{"hours": 1}` | 检查更新的间隔，有效的键有`weeks`、`days`、`hours`、`minutes`和`seconds` |

### Focus 对象

| 键     | 类型          | 默认值 | 解释                   |
| ------ | ------------- | ------ | ---------------------- |
| uid    | str           | 必填   | UP主的UID              |
| groups | Sequence[str] | `[]`   | 推送到的群的群号列表   |
| users  | Sequence[str] | `[]`   | 推送到的用户的QQ号列表 |
