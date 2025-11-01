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

# AI 聊天功能

## 使用方式

```
[回复历史消息]
[提问内容] @机器人
```

通过 AI 模型与机器人进行智能对话交流。

## 参数说明

| 参数         | 类型     | 是否必填 | 说明                                                | 示例                     | 默认值 |
| ------------ | -------- | -------- | --------------------------------------------------- | ------------------------ | ------ |
| 回复历史消息 | 回复操作 | 否       | 以回复链形式包含之前的对话内容                      | （直接回复机器人的消息） | 无     |
| 提问内容     | 文本     | 是       | 你想询问或交流的内容                                | `你好，今天天气怎么样？` | 无     |
| @机器人      | @操作    | 是       | 由于没有固定的触发关键词，需要在句子末尾明确@机器人 | `@机器人`                | 无     |

## 用户需求

### 积分要求

| 要求项 | 具体要求                                                              | 说明                 | 默认值 |
| ------ | --------------------------------------------------------------------- | -------------------- | ------ |
| 积分   | 积分数量需要大于等于当前上下文长度和模型预期输出 1k tokens 所需的积分 | 使用此功能会消耗积分 | `0`    |

## 回复格式

```
@你的昵称
[AI生成的回复内容]
-( 本次共消耗[使用积分数量]积分 )-
```

## 重要提示

1. 聊天内容的长度和上下文的长度都会影响积分的消耗
2. 不同的 AI 模型有不同的积分消耗比例
3. 如果上下文长度超过模型的最大限制，将无法完成请求
4. 如果您的积分不足，将无法完成请求
