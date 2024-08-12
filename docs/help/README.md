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

# QQ娱乐机器人命令指南

## 娱乐功能

这部分功能不使用数据库。

### 方舟功能

- `方舟抽卡` 朴素的十连
- `方舟十连` 华丽的十连

该功能由外部插件`nonebot-plugin-arkgacha`提供支持！  
如有疑问请查询该项目文档。

### 词云

- `/词云` 获取词云插件使用帮助(不受本系统控制)

本功能由外部插件`nonebot-plugin-wordcloud`提供支持！  
如有疑问请查询该项目文档。

## 用户相关

这部分功能会使用/修改全局数据库的内容

### AI

- `/llm <msg>` 和通义千问聊天   [详细文档](llm)
- `/prompt <msg>` 设置专属系统提示词    [详细文档](prompt)

### 关系系统

- `/wife` 随机获取**本群群友**作为老婆，当天**全局**互相绑定  [详细文档](wife)
- `/refresh` 消耗积分解除绑定     [详细文档](refresh)
- `/fork` 通过可信数据源导入关系数据    [详细文档](fork)
- `/renew` 续期关系     [详细文档](renew)

### 个人中心
- `/info [@someone]` 查看个人资料     [详细文档](info)
- `/sign` 每日签到获取积分    [详细文档](sign)
- `/transfer <@someone> <number>` 转账积分    [详细文档](transfer) 
- `/rank` 获取**全局**积分排行榜    [详细文档](rank)

### 超管系统

- `/grant <@someone>` 赋予用户超管权限  [详细文档](grant)
- `/bind <@A> <@B>` 绑定两个用户的关系  [详细文档](bind)
- `/charge <points>` 充值积分   [详细文档](charge)

## 调试功能

- `/init` 初始化数据库 **该命令仅@bot且有初始超管权限才能使用**
- `/members` 获取**本群**成员列表

## 温馨提醒

请不要设置过长的系统提示，或在大群中获取群成员列表，可能会导致较长延迟并影响自己和群员的体验。
