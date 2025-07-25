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

# 更改模型

```
更改模型 <模型ID>
```

切换AI聊天使用的模型

## 参数
| 参数     | 类型   | 必须 | 解释                     | 示例          | 默认 |
| -------- | ------ | ---- | ------------------------ | ------------- | ---- |
| `模型ID` | `text` | 是   | 要切换到的模型标识符     | `gpt-4o-mini` | 无   |

## 返回

### 切换成功
```
@sender
成功为您更换模型。
```

### 参数错误或模型不存在
```
@sender
请指定一个正确的目标模型。
支持的模型：

ID: {model_id}
名称: {model_name}
输入消耗倍率：{input_cost}
输出消耗倍率：{output_cost}
最大上下文长度：{context_length}
最长输出长度：{max_tokens} token
简介：{detail}

...

注：消耗计算方式：接口给出的消耗Token数/1000*倍率，消耗积分。
```

## 注意事项
1. 不同模型有不同的积分消耗率
2. 不同模型有不同的上下文长度限制
3. 切换模型后立即生效，影响后续的AI对话
4. 如果不提供参数或提供无效模型ID，会显示所有可用模型列表