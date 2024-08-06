from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent, Bot, GroupMessageEvent
from nonebot.params import CommandArg
import dashscope
from http import HTTPStatus
from random import randint
from .database import *
from . import config
from random import choice, randint
from datetime import datetime, timedelta

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

# [PUBLIC] Message Handler
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
            await autoReply.finish(
                MessageSegment.at(event.user_id)+
                '智能回复：'+
                response.output.choices[0].message.content # type: ignore
            )
        await autoReply.finish(MessageSegment.at(event.user_id)+f"错误：API服务器返回状态码{response.status_code}！") # type: ignore
    await autoReply.finish(MessageSegment.at(event.user_id)+f"系统消息：虽然你啥也没说，但是我记住你了！")

# [PUBLIC] `/setPrompt`
setPromptMatcher = on_command('prompt')
@setPromptMatcher.handle()
async def setPrompt(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(event.user_id, bot)
    user.system_prompt = args.extract_plain_text()
    await updateUser(user)
    await setPromptMatcher.finish(MessageSegment.at(event.user_id)+'已尝试更新您的专属系统提示词')

# [PUBLIC] `/getInformation`
getInformationMatcher = on_command('info')
@getInformationMatcher.handle()
async def getInformation(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(
        int(args['at',0].data['qq'] if args['at'] else event.user_id),
        bot
    )
    if couple := await user.couple:
        coupleUser = await getUserFromId(int(couple), bot)
    else: coupleUser = User(id="-1", nick="未绑定")
    if cp := await findCouple(user.id):
        expire = cp.date+timedelta(1)
    else: expire = datetime(1970,1,1,0,0,0,1)
    await getInformationMatcher.finish(
        MessageSegment.at(event.user_id)+
        f'''
{user.id}的用户信息：
昵称：{user.nick}
积分：{user.coins} {"本日已签到" if user.last_signed_date>=datetime.today()-timedelta(1) else "本日未签到"}
权限等级：{user.permission}
系统提示词：{user.system_prompt}
头像：'''
        +
        MessageSegment.image(await user.avatar)
        +
        f'本日老婆：{coupleUser.nick} ({coupleUser.id}) 失效时间：{expire.strftime("%Y/%m/%d %H:%M:%S")}'
    )

# [SUPER] `/grantPermission`
grantPermissionMatcher = on_command('grant')
@grantPermissionMatcher.handle()
async def grantPermission(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(event.user_id, bot)
    if user.permission>1:
        target = await getUserFromId(int(args["at",0].data["qq"]), bot)
        target.permission = max(user.permission-1, target.permission)
        await updateUser(target)
        await grantPermissionMatcher.finish(MessageSegment.at(event.user_id)+"已尝试授权.")
    await grantPermissionMatcher.finish(MessageSegment.at(event.user_id)+"授权者权限不足")

# [SUPER] `/bind`
bindMatcher = on_command('bind')
@bindMatcher.handle()
async def bind(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    if (await getUserFromId(event.user_id, bot)).permission>0:
        await useCouple(args['at',0].data['qq'],args['at',1].data['qq'])
        await bindMatcher.finish(MessageSegment.at(event.user_id)+'已尝试绑定CP！')
    await bindMatcher.finish(MessageSegment.at(event.user_id)+'权限不足！请找超管提权')

# [PUBLIC] `/wife`
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
        MessageSegment.at(event.user_id)+
        '\n你今天的老婆是：'+
        MessageSegment.image(await myWifeInfo.avatar)+
        f'{myWifeInfo.nick} ({myWifeInfo.id})\n\n今日关系已绑定，要好好珍惜哦！'
    )

# [PUBLIC] `/groupMembers`
groupMembersMatcher = on_command('members')
@groupMembersMatcher.handle()
async def groupMembers(event:GroupMessageEvent, bot:Bot):
    await groupMembersMatcher.finish(
        MessageSegment.at(event.user_id)+
        (
            '\n'.join(
                [
                    f"{x['nickname']} ({x['user_id']})"
                    for x in (
                        await bot.get_group_member_list(
                            group_id=event.group_id
                        )
                    )
                ]
            )
        )
    )

# [PUBLIC] `/sign`
signMatcher = on_command('sign')
@signMatcher.handle()
async def sign(event:MessageEvent, bot:Bot):
    user = await getUserFromId(event.user_id, bot)
    if user.last_signed_date <= datetime.today()-timedelta(1):
        coins = randint(config.daily_sign_min_coins, config.daily_sign_max_coins)
        user.coins += coins
        user.last_signed_date = datetime.now()
        await updateUser(user)
        await signMatcher.finish(MessageSegment.at(event.user_id)+f'签到成功！本次获得{coins}个积分')
    await signMatcher.finish(MessageSegment.at(event.user_id)+"本日已签到！请勿重复签到")

# [PUBLIC] `/rank`
rankMatcher = on_command('rank')
@rankMatcher.handle()
async def rank(event:MessageEvent):
    users = await getTop10Users()
    await rankMatcher.finish(
        MessageSegment.at(event.user_id)+
        '积分排行榜：\n'+
        (
            '\n'.join(
                [
                    f'[{x+1}] {users[x].nick} ({users[x].id}) : {users[x].coins}'
                    for x in range(len(users))
                ]
            )
        )
    )

# [PUBLIC] `/refresh`
refreshMatcher = on_command('refresh')
@refreshMatcher.handle()
async def refresh(event:MessageEvent, bot:Bot):
    user = await getUserFromId(event.user_id, bot)
    if user.coins>=config.refresh_price:
        await rmCouple(user.id, await user.couple)
        user.coins -= config.refresh_price
        await updateUser(user)
        await refreshMatcher.finish(MessageSegment.at(event.user_id)+f'已花费{config.refresh_price}积分解除绑定！')
    await refreshMatcher.finish(MessageSegment.at(event.user_id)+f'积分不足，需花费{config.refresh_price}积分.')
