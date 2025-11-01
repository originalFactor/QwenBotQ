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

# 设置 AI 系统提示词

## 使用方式

```
设置系统提示词 <提示词内容>
```

用于为 AI 聊天功能设置自定义的系统提示词，从而改变 AI 的回复风格和行为模式。

## 参数说明

| 参数       | 类型 | 是否必填 | 说明                       | 示例                 | 默认值 |
| ---------- | ---- | -------- | -------------------------- | -------------------- | ------ |
| 提示词内容 | 文本 | 是       | 要设置的系统提示词文本内容 | `你是一个友善的助手` | 无     |

## 回复格式

### 设置成功时

```
@你的昵称
成功为您设置系统提示词。
```

### 参数错误时

```
@你的昵称
请指定一个系统提示词。
```

## 重要提示

1. 系统提示词会直接影响 AI 的回复风格和行为模式
2. 设置完成后立即生效，会影响后续所有的 AI 对话
3. 提示词内容建议清晰明确，避免使用过于复杂或自相矛盾的指令
4. 如果不提供提示词内容，系统会提示您指定具体内容
