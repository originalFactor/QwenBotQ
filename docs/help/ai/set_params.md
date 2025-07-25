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

# 设置参数

```
设置参数 <参数名> <数值>
```

设置AI模型的生成参数

## 参数
| 参数     | 类型    | 必须 | 解释                                           | 示例   | 默认 |
| -------- | ------- | ---- | ---------------------------------------------- | ------ | ---- |
| `参数名` | `text`  | 是   | 要设置的参数名称（温度/频率惩罚/重复惩罚）     | `温度` | 无   |
| `数值`   | `float` | 是   | 参数的数值，通常在0.0-2.0之间                  | `0.7`  | 无   |

## 支持的参数
- **温度**：控制生成文本的随机性，值越高越随机
- **频率惩罚**：降低重复使用相同词汇的概率
- **重复惩罚**：降低重复相同内容的概率

## 返回
```
@sender
已尝试设定
```

## 注意事项
1. 参数值建议在合理范围内设置（0.0-2.0）
2. 温度过高可能导致生成内容不连贯
3. 惩罚值过高可能导致生成内容过于简短