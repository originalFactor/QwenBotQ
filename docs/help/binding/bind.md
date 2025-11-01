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

# 强制绑定 CP 关系

## 使用方式

```
官宣 <@用户A> <@用户B>
```

超管可以使用此命令强制将两个用户绑定为 CP 关系。

## 参数说明

| 参数    | 类型  | 是否必填 | 说明                 | 示例  | 默认值 |
| ------- | ----- | -------- | -------------------- | ----- | ------ |
| @用户 A | @提及 | 是       | 需要绑定的第一个用户 | @张三 | 无     |
| @用户 B | @提及 | 是       | 需要绑定的第二个用户 | @李四 | 无     |

## 权限要求

| 属性     | 要求                 | 说明                   | 默认值 |
| -------- | -------------------- | ---------------------- | ------ |
| 权限等级 | >= 1                 | 只有超管可以使用此命令 | 0      |
| 消耗积分 | >= bind_cost(默认 1) | 执行命令需要消耗的积分 | 0      |

## 回复格式

```
@你的昵称
已尝试绑定
{用户A昵称} ({用户AID})
和
{用户B昵称} ({用户BID})
为本日CP！
有效期至：YYYY/MM/DD
```
