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

# 恢复 CP 绑定关系

## 使用方式

```
回复一条消息并发送：恢复记录
```

从系统配置的可信来源导入 CP 绑定关系数据（常用于找回之前的 CP 关系）。

## 参数说明

| 参数     | 类型     | 是否必填 | 说明                               | 示例                   | 默认值 |
| -------- | -------- | -------- | ---------------------------------- | ---------------------- | ------ |
| 回复消息 | 回复操作 | 是       | 需要回复一条包含绑定关系信息的消息 | 回复一条可信来源的消息 | 无     |
| @发送者  | @提及    | 否       | QQ 会自动@发送者，此参数会被忽略   | @某人                  | 无     |

## 特殊说明

回复的消息发送者必须在系统配置文件中设置为可信来源，同时消息内容需要符合特定格式：

例如：

```
@用户1
你今天的群友老婆是
用户名 (1234567)
```

系统会自动将消息中第一个被@的用户（如上例中的`@用户1`）和第一个英文括号内的 QQ 号用户（如上例中的`1234567`）绑定在一起。

请注意：如果消息格式不符合要求，可能导致绑定失败！因此请谨慎设置可信来源。

## 积分要求

| 属性     | 要求                 | 说明                     | 默认值 |
| -------- | -------------------- | ------------------------ | ------ |
| 消耗积分 | >= fork_cost(默认 1) | 执行此命令需要消耗的积分 | 0      |

## 回复格式

```
@你的昵称
已成功绑定
{用户A昵称} ({用户AID})
和
{用户B昵称} ({用户BID})
的关系！(来自可信来源的外部数据)
过期时间：YYYY/MM/DD
```
