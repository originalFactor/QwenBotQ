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

# 恢复记录

```
<message>
[@sender] 恢复记录
```

从可信来源导入数据（可用于找回老婆）

## 参数
| 参数      | 类型    | 必须 | 解释                                              | 示例       | 默认 |
| --------- | ------- | ---- | ------------------------------------------------- | ---------- | ---- |
| `message` | `reply` | 是   | 回复一条信息                                      | 参见下方   | 无   |
| `@sender` | `at`    | 否   | 默认情况下，回复时QQ会自动@发送者，该参数会被忽略 | `@someone` | 无   |

### 特殊阐述

`message`的发送者必须在配置文件中规定的可信来源中，与此同时对消息内容也有要求。

例如：
```
@user1
你今天的群友老婆是
XXXXX (1234567)
```

第一个提及用户（此处为`@user1`，作为`a`）和第一对英文括号内QQ号用户（此处是`1234567`，作为`b`）将被绑定。

若格式不符合很可能出错！因此请谨慎设置信任来源。

## 其他需求

### 发送人用户信息
| 属性 | 要求                    | 解释     | 默认 |
| ---- | ----------------------- | -------- | ---- |
| 积分 | >= `fork_cost`(默认`1`) | 消耗积分 | `0`  |

## 返回
```
@sender
已成功绑定
{a.nick} ({a.id})
和
{b.nick} ({b.id})
的关系！(来自可信来源的外部数据)
```