# Copyright (C) 2024 originalFactor
# 
# This file is part of QwenBotQ.
# 
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

from typing import Union, Annotated, List
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from nonebot.adapters.onebot.v11.event import Sender
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from pydantic import BaseModel
from enum import Enum
from .database import *

# Get user nick
async def nick(user:User, bot:Bot)->str:
    if not(_ := await getNick(user.id)):
        _ = NickCache(
            id=user.id,
            nick=(await bot.get_stranger_info(
                user_id=int(user.id)
            ))['nickname'],
            created=datetime.now()
        )
        await useNick(_)
    return _.nick

# convert user into userwithnick
async def u2uwn(user:User, bot:Bot)->UserWithNick:
    return UserWithNick(**user.model_dump(),nick=await nick(user,bot))

# permission dependency
def require(cost_permission:int=0, cost_coins:int=0):
    async def _require(matcher:Matcher, event: GroupMessageEvent, bot:Bot)->UserWithNick:
        user = await getUser(event.user_id)
        if user.permission < cost_permission:
            await matcher.finish(
                (await at(user.id))+
                f'\n你的权限等级不足，需要{cost_permission}以上才能使用本功能'
            )
        if cost_coins:
            if user.coins < cost_coins:
                await matcher.finish(
                    (await at(user.id))+
                    f'\n你的积分不足，需要至少{cost_coins}积分才能使用本功能'
                )
            user.coins -= cost_coins
            await updateUser(user)
            await matcher.send(
                (await at(user.id))+
                f'\n你已被扣除{cost_coins}点积分以使用本功能'
            )
        return await u2uwn(user, bot)
    return _require

# plain text command argument dependency
def arg(tp:type):
    async def _arg(
            matcher:Matcher, 
            args:Annotated[Message, CommandArg()],
            event:GroupMessageEvent
            )->tp:
        try:
            return tp(args.extract_plain_text().strip())
        except:
            await matcher.finish(
                (await at(event.user_id))+
                f'\n请输入合法的{tp}类型参数！'
            )
    return _arg

# quick at
async def at(id:Union[str, int])->MessageSegment:
    return MessageSegment.at(int(id))

# users atted
def mentioned(least:int=0):
    async def _mentioned(
        matcher:Matcher, 
        bot:Bot, 
        args:Annotated[Message,CommandArg()],
        event:GroupMessageEvent
    )->List[UserWithNick]:
        mentioned_users = list([await u2uwn(await getUser(_.data['qq']), bot) for _ in args['at']])
        if len(mentioned_users)<least:
            await matcher.finish(
                (await at(event.user_id))+
                f'\n该功能至少要提及{least}个用户。'
            )
        return mentioned_users
    return _mentioned

class MessageType(str, Enum):
    private = "private"
    group = "group"
class GetMsgResult(BaseModel):
    time : int
    message_type : MessageType
    message_id : int
    real_id : int
    sender : Sender
    message : Message

# reply dependency
def reply(required:bool=False):
    async def _reply(matcher:Matcher, bot:Bot, event:GroupMessageEvent)->Union[GetMsgResult,None]:
        if required and not event.original_message['reply']:
            await matcher.finish(
                (await at(event.user_id))+
                "\n必须回复一条消息才能使用此功能"
            )
        return (
            GetMsgResult(
                **(
                    await bot.get_msg(
                        message_id=event.original_message['reply',0].data['id']
                    )
                )
            )
            if event.original_message['reply'] 
            else None
        )
    return _reply
