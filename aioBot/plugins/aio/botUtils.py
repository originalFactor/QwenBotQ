from typing import Union, Annotated, List
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends
from .database import *

# Get user nick
async def getNick(id:Union[str, int], bot:Bot):
    return (await bot.get_stranger_info(
        user_id=int(id)
    ))['nickname']

# Get user
async def getUserFromId(id:Union[str, int], bot:Bot)->User:
    if not (user := await getUser(str(id))):
        user = User(
            id=str(id),
            nick=await getNick(id, bot)
        )
        await createUser(user)
    if not user.nick:
        user.nick = await getNick(id, bot)
        await updateUser(user)
    return user

# permission dependency
def require(cost_permission:int=0, cost_coins:int=0):
    async def _require(matcher:Matcher, event: GroupMessageEvent, bot:Bot)->User:
        user = await getUserFromId(event.user_id, bot)
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
        return user
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
    )->List[User]:
        mentioned_users = list([await getUserFromId(_.data['qq'], bot) for _ in args['at']])
        if len(mentioned_users)<least:
            await matcher.finish(
                (await at(event.user_id))+
                f'\n该功能至少要提及{least}个用户。'
            )
        return mentioned_users
    return _mentioned
