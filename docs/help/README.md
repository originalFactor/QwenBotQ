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

- `词云` 获取词云插件使用帮助(不受本系统控制)

本功能由外部插件`nonebot-plugin-wordcloud`提供支持！  
如有疑问请查询该项目文档。

### 表情包

- `表情包制作` 查看可用表情包列表，图标是图像的代表需要带图，可@某人用其头像作为图片
- `表情详情 表情名称`
- `表情名称 参数` 制作表情，参数为图片或文字

## 用户相关

这部分功能会使用/修改全局数据库的内容

### AI

- `@bot <msg>` 和通义千问聊天   [详细文档](llm)
- `设置系统提示词 <msg>` 设置专属系统提示词    [详细文档](prompt)

### 关系系统

- `今日老公` 随机获取**本群群友**老公，当天**全局**互相绑定  [详细文档](wife)
- `我不要和他玩` 消耗积分解除绑定     [详细文档](refresh)
- `我要这个` 通过可信数据源导入关系数据    [详细文档](fork)
- `还要这个` 续期关系     [详细文档](renew)

### 个人中心
- `用户信息 [@someone]` 查看个人资料     [详细文档](info)
- `签到` 每日签到获取积分    [详细文档](sign)
- `转账给 <@someone> <number>` 转账积分    [详细文档](transfer) 
- `封神榜` 获取**全局**积分排行榜    [详细文档](rank)

### 超管系统

- `授予权限 <@someone>` 赋予用户超管权限  [详细文档](grant)
- `捆在一起 <@A> <@B>` 绑定两个用户的关系  [详细文档](bind)
- `印钞机 <number>` 充值积分   [详细文档](charge)

### 调试功能

- `删库跑路` 初始化数据库 **该命令仅@bot且有初始超管权限才能使用**
- `群友列表` 获取**本群**成员列表

### 其他功能

- `说明书` 显示介绍

## 温馨提醒

请不要设置过长的系统提示，或在大群中获取群成员列表，可能会导致较长延迟并影响自己和群员的体验。
