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

# 设置系统提示词

```
设置系统提示词 <提示词内容>
```

为AI聊天设置自定义的系统提示词，影响AI的回复风格和行为

## 参数
| 参数         | 类型   | 必须 | 解释                           | 示例                     | 默认 |
| ------------ | ------ | ---- | ------------------------------ | ------------------------ | ---- |
| `提示词内容` | `text` | 是   | 要设置的系统提示词文本         | `你是一个友善的助手`     | 无   |

## 返回

### 设置成功
```
@sender
成功为您设置系统提示词。
```

### 参数错误
```
@sender
请指定一个系统提示词。
```

## 注意事项
1. 系统提示词会影响AI的回复风格和行为模式
2. 设置后立即生效，影响后续的AI对话
3. 提示词内容应该清晰明确，避免过于复杂或矛盾的指令
4. 如果不提供参数，会提示用户指定提示词内容