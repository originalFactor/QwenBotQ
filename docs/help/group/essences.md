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

# 查看群精华列表

## 使用方式

```
精华列表
```

用于获取当前群组的所有精华消息列表。

## 参数说明

无参数要求，直接发送命令即可。

## 回复格式

```
@你的昵称
群精华列表：
{消息发送者昵称} ({消息发送者ID})：
{消息内容}
由 {设置者昵称} ({设置者ID}) 于
    {设置时间} 设置。

{消息发送者昵称} ({消息发送者ID})：
{消息内容}
由 {设置者昵称} ({设置者ID}) 于
    {设置时间} 设置。
...
```

## 重要提示

1. 此功能只能在群聊中使用
2. 会显示群内所有精华消息的详细信息
3. 包括消息发送者、内容、设置者和设置时间
4. 如果群内没有精华消息，将返回空列表
