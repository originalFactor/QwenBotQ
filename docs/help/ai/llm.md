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

# AI 聊天

```
[message]
<prompt> <@bot>
```

使用AI模型进行聊天对话

## 参数
| 参数      | 类型    | 必须 | 解释                                     | 示例    | 默认 |
| --------- | ------- | ---- | ---------------------------------------- | ------- | ---- |
| `message` | `reply` | 否   | 历史消息，以回复链方式存在               | 见下方  | 无   |
| `prompt`  | `text`  | 是   | 本次的提示词                             | `Hello` | 无   |
| `@bot`    | `at`    | 是   | 由于无触发关键词，需句尾显式@bot方可激活 | `@bot`  | 无   |

## 其他需求

### 发送人用户信息
| 属性 | 要求                                                       | 解释     | 默认 |
| ---- | ---------------------------------------------------------- | -------- | ---- |
| 积分 | >= 当前上下文长度和模型预期输出1k tokens情况下需消耗积分量 | 消耗积分 | `0`  |

## 返回
```
@sender
{content}
-( 本次共消耗{usage}积分 )-
```

## 注意事项
1. 聊天内容长度和上下文长度会影响积分消耗
2. 不同模型有不同的积分消耗率
3. 如果上下文长度超过模型限制，将无法完成请求
4. 如果积分不足，将无法完成请求