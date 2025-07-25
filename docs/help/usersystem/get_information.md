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

# 用户信息

```
用户信息 [@用户]
```

查看用户的详细信息

## 参数
| 参数   | 类型 | 必须 | 解释                           | 示例     | 默认     |
| ------ | ---- | ---- | ------------------------------ | -------- | -------- |
| `@用户` | `at` | 否   | 要查看信息的用户，不填则查看自己 | `@12345` | 发送者自己 |

## 返回
```
@sender
{user_id}的用户信息：
昵称：{nickname}
稀有度：{bind_power}
积分：{coins}
    已签到/未签到
    失效日期：YYYY/MM/DD
权限等级：{permission}
使用模型：{model}
    系统提示词：{system_prompt}...
    温度：{temperature}
    频率惩罚：{frequency_penalty}
    重复惩罚：{presence_penalty}
头像：[用户头像图片]
本日老公：{cp_nick} ({cp_id})/未绑定
    失效日期：YYYY/MM/DD
```

## 注意事项
1. 稀有度影响被随机选为老公的概率
2. 积分用于各种功能的消耗
3. 权限等级决定可使用的功能
4. 模型参数影响AI回复的风格