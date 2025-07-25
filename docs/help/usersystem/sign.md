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

# 签到

```
签到
```

每日签到获取积分奖励

## 返回

### 签到成功
```
@sender
签到成功！本次获得{coins}个积分
过期时间：YYYY/MM/DD
```

### 重复签到
```
@sender
本日已签到！请勿重复签到！
最近一次签到的过期时间：
YYYY/MM/DD
```

## 注意事项
1. 每日只能签到一次
2. 签到获得的积分数量是随机的，在配置的最小值和最大值之间
3. 签到有效期为24小时
4. 积分可用于AI聊天、绑定关系等功能