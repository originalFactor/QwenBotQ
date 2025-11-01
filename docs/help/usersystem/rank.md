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

# 查看积分排行榜

## 使用方式

```
积分榜
```

用于查看机器人所有用户中的积分排行榜前 10 名。

## 参数说明

无参数要求，直接发送命令即可。

## 回复格式

```
@你的昵称
积分排行榜：
[1] {用户昵称} ({用户ID}) : {积分数量}
[2] {用户昵称} ({用户ID}) : {积分数量}
...
[10] {用户昵称} ({用户ID}) : {积分数量}
```

## 重要提示

1. 排行榜仅显示积分最高的前 10 名用户
2. 用户按积分数量从高到低排序显示
3. 当多个用户积分相同时，按用户 ID 进行排序
