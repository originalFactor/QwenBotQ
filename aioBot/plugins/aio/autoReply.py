from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent, Bot, GroupMessageEvent
from nonebot.params import CommandArg
import dashscope
from http import HTTPStatus
from random import randint
from . import config
from .database import getUser, createUser, User, updateUser, useCouple
from random import choice
from datetime import datetime

# Initialize Dashscope Api Key
dashscope.api_key = config.dashscope_api_key

# Get user nick
async def getNick(id:int, bot:Bot):
    return (await bot.get_stranger_info(
        user_id=id
    ))['nickname']

# Get user
async def getUserFromId(id:int, bot:Bot)->User:
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

# [PRIVATE] Message Handler
autoReply = on_command('llm')
@autoReply.handle()
async def autoReplyHandler(bot:Bot, event:MessageEvent, args:Message = CommandArg()):
    userRequest = args.extract_plain_text()
    user = await getUserFromId(event.user_id, bot)
    if userRequest:
        response = dashscope.Generation.call(
            model="qwen-max-longcontext",
            messages=[
                {'role': 'system', 'content': user.system_prompt}, # type: ignore
                {'role': 'user', 'content': userRequest}
            ],
            seed=randint(1,10000),
            temprature=0.8,
            top_p=0.8,
            top_k=50,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK: # type: ignore
            await autoReply.finish('智能回复：'+response.output.choices[0].message.content) # type: ignore
        await autoReply.finish(f"错误：API服务器返回状态码{response.status_code}！") # type: ignore
    await autoReply.finish(f"系统消息：虽然你啥也没说，但是我记住你了！")

# [PRIVATE] `/setPrompt`
setPromptMatcher = on_command('setPrompt')
@setPromptMatcher.handle()
async def setPrompt(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(event.user_id, bot)
    user.system_prompt = args.extract_plain_text()
    await updateUser(user)
    await setPromptMatcher.finish('已尝试更新您的专属系统提示词')

# [DEBUG] `/getInformation`
getInformationMatcher = on_command('getInformation')
@getInformationMatcher.handle()
async def getInformation(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(
        int(args['at',0].data['qq'] if args['at'] else event.user_id),
        bot
    )
    couple = await user.couple
    if not couple: couple = '未绑定'
    await getInformationMatcher.finish(
        f'''{user.id}的用户信息：
昵称：{user.nick}
权限等级：{user.permission}
系统提示词：{user.system_prompt}
头像：'''
        +
        MessageSegment.image(await user.avatar)
        +
        f'本日老婆：{couple}'
    )

# [PRIVATE] [SUPER] `/grantPermission`
grantPermissionMatcher = on_command('grantPermission')
@grantPermissionMatcher.handle()
async def grantPermission(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(event.user_id, bot)
    if user.permission>1:
        target = await getUserFromId(int(args["at",0].data["qq"]), bot)
        target.permission = max(user.permission-1, target.permission)
        await updateUser(target)
        await grantPermissionMatcher.finish("已尝试授权.")
    await grantPermissionMatcher.finish("授权者权限不足")

# [PRIVATE] [SUPER] `/bind`
bindMatcher = on_command('bind')
@bindMatcher.handle()
async def bind(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    if (await getUserFromId(event.user_id, bot)).permission>0:
        await useCouple(args['at',0].data['qq'],args['at',1].data['qq'])
        await bindMatcher.finish('已尝试绑定CP！')
    await bindMatcher.finish('权限不足！请找超管提权')

# [PRIVATE] `/wife`
wifeMatcher = on_command('wife')
@wifeMatcher.handle()
async def wife(event:GroupMessageEvent, bot:Bot):
    user = await getUserFromId(event.user_id, bot)
    if myWife := await user.couple:
        myWifeInfo = await getUserFromId(int(myWife), bot)
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        myWifeInfo = User(id=str(x['user_id']), nick=x['nickname'])
        await useCouple(str(event.user_id),str(myWifeInfo.id))
    await wifeMatcher.finish(
        f'你今天的老婆是：{myWifeInfo.nick}'+MessageSegment.image(await myWifeInfo.avatar)+'今日关系已绑定，要好好珍惜哦！'
    )

# [PRIVATE] `/groupMembers`
groupMembersMatcher = on_command('groupMembers')
@groupMembersMatcher.handle()
async def groupMembers(event:GroupMessageEvent, bot:Bot):
    await groupMembersMatcher.finish('\n'.join([x['nickname'] for x in (await bot.get_group_member_list(group_id=event.group_id))]))
