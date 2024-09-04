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

# `授予权限 <@someone>`

消耗积分将指定用户授权为小于自己权限一级的管理。
默认情况下初始超管（最高权限）的等级是999。

## 参数
| 参数       | 类型 | 必须 | 解释     | 示例     | 默认 |
| ---------- | ---- | ---- | -------- | -------- | ---- |
| `@someone` | `at` | 是   | 目标对象 | 参见下方 | 无   |

## 其他需求

### 发送人用户信息
| 属性 | 要求                     | 解释     | 默认 |
| ---- | ------------------------ | -------- | ---- |
| 积分 | >= `grant_cost`(默认`1`) | 消耗积分 | `0`  |
| 权限 | >= `2`                   | 所需权限 | `0`  |

## 返回
```
@sender
已成功授予{someone.permission}级权限给
{someone.nick} ({someone.id})
```