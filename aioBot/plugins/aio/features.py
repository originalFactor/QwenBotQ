from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent, Bot, GroupMessageEvent
from nonebot.params import CommandArg
import dashscope
from http import HTTPStatus
from random import randint, choice
from .database import *
from .utils import *
from . import config

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
                '\n智能回复：\n'+
                response.output.choices[0].message.content # type: ignore
            )
        await autoReply.finish(MessageSegment.at(event.user_id)+f"\n错误：API服务器返回状态码{response.status_code}！") # type: ignore
    await autoReply.finish(MessageSegment.at(event.user_id)+f"\n系统消息：虽然你啥也没说，但是我记住你了！")

# [PUBLIC] `/setPrompt`
setPromptMatcher = on_command('prompt')
@setPromptMatcher.handle()
async def setPrompt(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(event.user_id, bot)
    user.system_prompt = args.extract_plain_text()
    await updateUser(user)
    await setPromptMatcher.finish(MessageSegment.at(event.user_id)+'\n已尝试更新您的专属系统提示词')

# [PUBLIC] `/getInformation`
getInformationMatcher = on_command('info')
@getInformationMatcher.handle()
async def getInformation(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    user = await getUserFromId(
        int(args['at',0].data['qq'] if args['at'] else event.user_id),
        bot
    )
    if couple := await user.couple:
        coupleUser = await getUserFromId(
            int(await couple.opposite(event.get_user_id())),
            bot
        )
    await getInformationMatcher.finish(
        MessageSegment.at(event.user_id)+
        '\n{id}的用户信息：\n'
        '昵称：{nick}\n'
        '积分：{coins}\n'
        '\t{signStatus}\n'
        '权限等级：{permission}\n'
        '系统提示词：{system_prompt}\n'
        '头像：'.format(
            id=user.id,
            nick=user.nick,
            coins=user.coins,
            signStatus=(
                '已签到\n\t失效时间：{}'.format((await user.sign_expire).strftime('%Y/%m/%d %H:%M:%S'))
                if await stillVaild(user.last_signed_date) else
                '未签到'
            ),
            permission=user.permission,
            system_prompt=user.system_prompt
        )+
        MessageSegment.image(await user.avatar)+
        '本日老婆：'+
        (
            f'{coupleUser.nick} ({coupleUser.id})\n'
            f'\t失效时间：{(await couple.expire).strftime("%Y/%m/%d %H:%M:%S")}'
            if couple else
            '未绑定'
        )
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
        await grantPermissionMatcher.finish(MessageSegment.at(event.user_id)+"\n已尝试授权.")
    await grantPermissionMatcher.finish(MessageSegment.at(event.user_id)+"\n授权者权限不足")

# [SUPER] `/bind`
bindMatcher = on_command('bind')
@bindMatcher.handle()
async def bind(event:MessageEvent, bot:Bot, args:Message = CommandArg()):
    if (await getUserFromId(event.user_id, bot)).permission>0:
        await useCouple(Couple(A=args['at',0].data['qq'],B=args['at',1].data['qq'],date=datetime.now()))
        await bindMatcher.finish(MessageSegment.at(event.user_id)+'\n已尝试绑定CP！')
    await bindMatcher.finish(MessageSegment.at(event.user_id)+'\n权限不足！请找超管提权')

# [PUBLIC] `/wife`
wifeMatcher = on_command('wife')
@wifeMatcher.handle()
async def wife(event:GroupMessageEvent, bot:Bot):
    user = await getUserFromId(event.user_id, bot)
    if myWife := await user.couple:
        myWifeInfo = await getUserFromId(int(await myWife.opposite(event.get_user_id())), bot)
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        myWifeInfo = await getUserFromId(int(x['user_id']), bot)
        await useCouple(Couple(A=event.get_user_id(),B=myWifeInfo.id,date=datetime.now()))
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
        MessageSegment.at(event.user_id)+'\n'+
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
    if not stillVaild(user.last_signed_date):
        coins = randint(config.daily_sign_min_coins, config.daily_sign_max_coins)
        user.coins += coins
        user.last_signed_date = datetime.now()
        await updateUser(user)
        await signMatcher.finish(MessageSegment.at(event.user_id)+f'\n签到成功！本次获得{coins}个积分')
    await signMatcher.finish(MessageSegment.at(event.user_id)+"\n本日已签到！请勿重复签到")

# [PUBLIC] `/rank`
rankMatcher = on_command('rank')
@rankMatcher.handle()
async def rank(event:MessageEvent):
    users = await getTop10Users()
    await rankMatcher.finish(
        MessageSegment.at(event.user_id)+
        '\n积分排行榜：\n'+
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
        if couple := await user.couple:
            await rmCouple(couple)
            user.coins -= config.refresh_price
            await updateUser(user)
            await refreshMatcher.finish(MessageSegment.at(event.user_id)+f'\n已花费{config.refresh_price}积分解除绑定！')
        await refreshMatcher.finish(MessageSegment.at(event.user_id)+f'\n未绑定对象，无需解绑！')
    await refreshMatcher.finish(MessageSegment.at(event.user_id)+f'\n积分不足，需花费{config.refresh_price}积分.')
