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

# 随机精华

```
随机精华
```

从当前群组的精华消息中随机获取一条

## 返回
```
@sender
随机群精华：
{sender_nick} ({sender_id})：
{message_content}
由 {operator_nick} ({operator_id}) 于
    {operator_time} 设置。
```

## 注意事项
1. 只能在群聊中使用
2. 从群内所有精华消息中随机选择一条
3. 如果群内没有精华消息，可能会出错
4. 显示消息发送者、内容、设置者和设置时间