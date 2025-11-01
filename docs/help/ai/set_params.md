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

# 设置 AI 模型参数

## 使用方式

```
设置参数 <参数名> <数值>
```

用于调整 AI 模型的生成参数，优化 AI 回复效果。

## 参数说明

| 参数   | 类型   | 是否必填 | 说明                                             | 示例   | 默认值 |
| ------ | ------ | -------- | ------------------------------------------------ | ------ | ------ |
| 参数名 | 文本   | 是       | 要设置的参数名称，可选：温度、频率惩罚、重复惩罚 | `温度` | 无     |
| 数值   | 浮点数 | 是       | 参数的具体数值，通常建议在 0.0-2.0 之间调整      | `0.7`  | 无     |

## 支持的参数说明

- **温度**：控制 AI 生成内容的随机性，数值越高，生成的内容越随机多样
- **频率惩罚**：降低 AI 重复使用相同词汇的概率，使表达更加丰富
- **重复惩罚**：降低 AI 重复相同内容的概率，避免过于单调的回复

## 回复格式

```
@你的昵称
已尝试设定
```

## 重要提示

1. 参数值建议在 0.0-2.0 的合理范围内调整
2. 温度值过高可能会导致生成的内容不够连贯或偏离主题
3. 惩罚值过高可能会导致生成的内容过于简短，影响表达完整性
