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

# 印钞机

```
印钞机 <number>
```

## 参数
| 参数     | 类型  | 必须 | 解释         | 示例 | 默认 |
|----------|-------|------|--------------|------|------|
| `number` | `int` |  是  | 充值积分数量 | `1`  | 无   |

## 其他需求

### 发送人用户信息
| 属性 | 要求                          | 解释     | 默认 |
|------|-------------------------------|----------|------|
| 权限 | >= `charge_min_perm`(默认`1`) | 超管     | `0`  |

## 返回
```
@sender
已为您的账户充值{number}积分！
```
