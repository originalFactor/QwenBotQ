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

# 充值积分

## 使用方式

```
印钞机 <积分数量>
```

用于为自己的账户充值指定数量的积分。

## 参数说明

| 参数     | 类型 | 是否必填 | 说明               | 示例 | 默认值 |
| -------- | ---- | -------- | ------------------ | ---- | ------ |
| 积分数量 | 整数 | 是       | 需要充值的积分数量 | 1    | 无     |

## 权限要求

| 属性     | 要求                       | 说明                   | 默认值 |
| -------- | -------------------------- | ---------------------- | ------ |
| 权限等级 | >= charge_min_perm(默认 1) | 只有超管可以使用此命令 | 0      |

## 回复格式

```
@你的昵称
已为您的账户充值{积分数量}积分！
```
