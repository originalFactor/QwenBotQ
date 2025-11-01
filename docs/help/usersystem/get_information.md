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

# 查看用户信息

## 使用方式

```
用户信息 [@用户]
```

用于查看指定用户或自己的详细信息。

## 参数说明

| 参数  | 类型  | 是否必填 | 说明                             | 示例   | 默认值     |
| ----- | ----- | -------- | -------------------------------- | ------ | ---------- |
| @用户 | @提及 | 否       | 要查看信息的用户，不填则查看自己 | @12345 | 发送者自己 |

## 回复格式

```
@你的昵称
{用户ID}的用户信息：
昵称：{用户昵称}
稀有度：{稀有度数值}
积分：{积分数量}
    已签到/未签到
    失效日期：YYYY/MM/DD
权限等级：{权限等级数值}
使用模型：{当前使用模型}
    系统提示词：{系统提示词内容}...
    温度：{温度值}
    频率惩罚：{频率惩罚值}
    重复惩罚：{重复惩罚值}
头像：[用户头像图片]
本日CP：{CP昵称} ({CPID})/未绑定
    失效日期：YYYY/MM/DD
```

## 重要提示

1. 稀有度会影响被随机选为 CP 的概率
2. 积分用于使用各种功能时的消耗
3. 权限等级决定了您可以使用哪些功能
4. AI 模型参数会影响 AI 回复的风格和表现
