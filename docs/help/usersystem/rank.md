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

# 积分榜

```
积分榜
```

查看积分排行榜前10名

## 返回
```
@sender
积分排行榜：
[1] {nickname} ({user_id}) : {coins}
[2] {nickname} ({user_id}) : {coins}
...
[10] {nickname} ({user_id}) : {coins}
```

## 注意事项
1. 只显示前10名用户
2. 按积分数量从高到低排序
3. 积分相同时按用户ID排序