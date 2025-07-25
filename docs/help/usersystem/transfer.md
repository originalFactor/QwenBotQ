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

# 转账给

```
转账给 @用户 <积分数量>
```

向其他用户转账积分

## 参数
| 参数       | 类型  | 必须 | 解释               | 示例     | 默认 |
| ---------- | ----- | ---- | ------------------ | -------- | ---- |
| `@用户`    | `at`  | 是   | 要转账的目标用户   | `@12345` | 无   |
| `积分数量` | `int` | 是   | 要转账的积分数量   | `100`    | 无   |

## 返回

### 转账成功
```
@sender
成功给
{target_nick} ({target_id})
转账了{amount}积分！
```

### 转账失败
```
@sender
您的积分余额不足以转账{amount}积分！
```

### 其他错误
```
@sender
不允许反向转账积分！
```
或
```
@sender
不允许给自己转账！
```

## 注意事项
1. 转账数量不能为负数
2. 不能给自己转账
3. 转账前会检查余额是否充足
4. 转账成功后会立即扣除发送者积分并增加接收者积分