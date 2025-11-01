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

# 随机查看群精华

## 使用方式

```
随机精华
```

用于从当前群组的精华消息中随机获取并显示一条。

## 参数说明

无参数要求，直接发送命令即可。

## 回复格式

```
@你的昵称
随机群精华：
{消息发送者昵称} ({消息发送者ID})：
{消息内容}
由 {设置者昵称} ({设置者ID}) 于
    {设置时间} 设置。
```

## 重要提示

1. 此功能只能在群聊中使用
2. 系统会从群内所有精华消息中随机选择一条显示
3. 如果群内没有精华消息，可能会导致功能无法正常使用
4. 显示的信息包括消息发送者、内容、设置者和设置时间
