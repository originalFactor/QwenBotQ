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

# 转账积分给其他用户

## 使用方式

```
转账给 @用户 <积分数量>
```

将自己的积分转账给指定的其他用户。

## 参数说明

| 参数     | 类型  | 是否必填 | 说明               | 示例  | 默认值 |
| -------- | ----- | -------- | ------------------ | ----- | ------ |
| @用户    | @提及 | 是       | 需要转账的目标用户 | @某人 | 无     |
| 积分数量 | 数字  | 是       | 要转账的积分数量   | 100   | 无     |

## 回复格式

### 转账成功

```
@你的昵称
成功给
{目标用户昵称} ({目标用户ID})
转账了{转账积分数量}积分！
```

### 转账失败

```
@你的昵称
您的积分余额不足以转账{转账积分数量}积分！
```

### 其他错误

```
@你的昵称
不允许反向转账积分！
```

或

```
@你的昵称
不允许给自己转账！
```

## 重要提示

1. 转账的积分数量必须是正整数，不能为负数
2. 不能给自己转账积分
3. 转账前系统会自动检查您的积分余额是否足够
4. 转账成功后，系统会立即从您的账户扣除相应积分，并增加到接收者的账户中
