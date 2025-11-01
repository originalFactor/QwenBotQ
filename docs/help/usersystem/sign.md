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

# 每日签到

## 使用方式

```
签到
```

每天签到一次可获取随机积分奖励。

## 参数说明

无参数要求，直接发送命令即可。

## 回复格式

### 签到成功

```
@你的昵称
签到成功！本次获得{积分数量}个积分
过期时间：YYYY/MM/DD
```

### 重复签到

```
@你的昵称
本日已签到！请勿重复签到！
最近一次签到的过期时间：
YYYY/MM/DD
```

## 重要提示

1. 每个用户每天只能签到一次
2. 签到获得的积分数量是随机的，具体数值在机器人配置的最小值和最大值之间
3. 签到后需要等待 24 小时才能再次签到
4. 获得的积分可用于 AI 聊天、绑定关系等功能的消耗
