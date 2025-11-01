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

# 更改 AI 模型

## 使用方式

```
更改模型 <模型ID>
```

用于切换 AI 聊天功能使用的模型类型。

## 参数说明

| 参数    | 类型 | 是否必填 | 说明                       | 示例          | 默认值 |
| ------- | ---- | -------- | -------------------------- | ------------- | ------ |
| 模型 ID | 文本 | 是       | 要切换到的模型的唯一标识符 | `gpt-4o-mini` | 无     |

## 回复说明

### 切换成功时

```
@你的昵称
成功为您更换模型。
```

### 参数错误或模型不存在时

```
@你的昵称
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

注：积分消耗计算方式：接口返回的消耗Token数 ÷ 1000 × 倍率，结果即为消耗的积分数量。
```

## 重要提示

1. 不同的 AI 模型有不同的积分消耗比例
2. 不同的 AI 模型支持的上下文长度有所不同
3. 模型切换后立即生效，会影响后续所有的 AI 对话
4. 如果不提供参数或提供了无效的模型 ID，系统会自动显示所有可用的模型列表
