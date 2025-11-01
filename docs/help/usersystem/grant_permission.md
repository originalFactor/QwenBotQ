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

# 授予用户管理权限

## 使用方式

```
授予权限 <@用户>
```

消耗积分将指定用户授权为比自己权限低一级的管理员。
默认情况下，初始超管（最高权限）的等级是 3 级。

## 参数说明

| 参数  | 类型  | 是否必填 | 说明                   | 示例  | 默认值 |
| ----- | ----- | -------- | ---------------------- | ----- | ------ |
| @用户 | @提及 | 是       | 需要授予权限的目标用户 | @某人 | 无     |

## 权限要求

| 属性     | 要求                  | 说明                                        | 默认值 |
| -------- | --------------------- | ------------------------------------------- | ------ |
| 消耗积分 | >= grant_cost(默认 1) | 执行此命令需要消耗的积分                    | 0      |
| 权限等级 | >= 2                  | 只有权限等级 2 级及以上的用户可以使用此命令 | 0      |

## 回复格式

```
@你的昵称
已成功授予{用户权限等级}级权限给
{用户昵称} ({用户ID})
```
