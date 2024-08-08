from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, GroupMessageEvent
from nonebot.params import Depends
import dashscope
from http import HTTPStatus
from random import randint, choice
from typing import Annotated
from .database import *
from .utils import *
from .botUtils import *
from . import config

# Initialize Dashscope Api Key
dashscope.api_key = config.dashscope_api_key

# [PUBLIC] Message Handler
autoReply = on_command('llm')
@autoReply.handle()
async def autoReplyHandler(
        user:Annotated[User, Depends(require(0,config.llm_cost))], 
        request:Annotated[str, Depends(arg(str))]
        ):
    if request:
        response = dashscope.Generation.call(
            model="qwen-max-longcontext",
            messages=[
                {'role': 'system', 'content': user.system_prompt}, # type: ignore
                {'role': 'user', 'content': request}
            ],
            seed=randint(1,10000),
            temprature=0.8,
            top_p=0.8,
            top_k=50,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK: # type: ignore
            await updateUser(user)
            await autoReply.finish(
                (await at(user.id))+
                f'\n大模型回答：\n'+
                response.output.choices[0].message.content # type: ignore
            )
        await autoReply.finish(
            (await at(user.id))+
            f"\n错误：API服务器返回状态码{response.status_code}！" # type: ignore
        )
    await autoReply.finish(
        (await at(user.id))+
        f"\n系统消息：虽然你啥也没说，但是我记住你了！"
    )

# [PUBLIC] `/setPrompt`
setPromptMatcher = on_command('prompt')
@setPromptMatcher.handle()
async def setPrompt(
    user : Annotated[User, Depends(require(0,config.set_prompt_cost))],
    prompt : Annotated[str, Depends(arg(str))]
):
    user.system_prompt = prompt
    await updateUser(user)
    await setPromptMatcher.finish(
        (await at(user.id))+
        '\n已尝试更新您的专属系统提示词'
    )

# [PUBLIC] `/getInformation`
getInformationMatcher = on_command('info')
@getInformationMatcher.handle()
async def getInformation(
    send_user : Annotated[User, Depends(require())],
    mention : Annotated[List[User], Depends(mentioned())],
    bot : Bot
):
    user = mention[0] if mention else send_user
    if couple := await user.couple:
        coupleUser = await getUserFromId(
            (await couple.opposite(user.id)),
            bot
        )
    await getInformationMatcher.finish(
        (await at(user.id))+
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
async def grantPermission(
    user : Annotated[User, Depends(require(2,config.grant_cost))], 
    mention : Annotated[List[User], Depends(mentioned(1))]
):
    mention[0].permission = max(user.permission-1, mention[0].permission)
    await updateUser(mention[0])
    await grantPermissionMatcher.finish(
        (await at(user.id))+
        f"\n已授予{mention[0].permission}级权限给\n"+
        f'{mention[0].nick} ({mention[0].id})'
    )

# [SUPER] `/bind`
bindMatcher = on_command('bind')
@bindMatcher.handle()
async def bind(
    user : Annotated[User, Depends(require(1,config.bind_cost))],
    mention : Annotated[List[User], Depends(mentioned(2))]
):
    cp = Couple(A=mention[0].id,B=mention[1].id,date=datetime.now())
    await useCouple(cp)
    await bindMatcher.finish(
        (await at(user.id))+
        '\n已尝试绑定\n'
        f'{mention[0].nick} ({mention[0].id})\n'
        '和\n'
        f'{mention[1].nick} ({mention[1].id})\n'
        '为本日CP！\n'
        f'有效期至：{(await cp.expire).strftime("%Y/%m/%d %H:%M:%S")}'
    )

# [PUBLIC] `/wife`
wifeMatcher = on_command('wife')
@wifeMatcher.handle()
async def wife(
    user : Annotated[User, Depends(require())],
    event : GroupMessageEvent,
    bot : Bot
):
    if myWife := await user.couple:
        myWifeInfo = await getUserFromId(await myWife.opposite(user.id), bot)
    else:
        x = choice(await bot.get_group_member_list(group_id=event.group_id))
        myWifeInfo = await getUserFromId(x['user_id'], bot)
        myWife = Couple(A=user.id,B=myWifeInfo.id,date=datetime.now())
        await useCouple(myWife)
    await wifeMatcher.finish(
        (await at(user.id))+
        '\n你今天的老婆是：'+
        MessageSegment.image(await myWifeInfo.avatar)+
        f'{myWifeInfo.nick} ({myWifeInfo.id})\n'
        f'过期时间：{(myWife.date+timedelta(1)).strftime("%Y/%m/%d %H:%M:%S")}\n'
        '\n今日关系已绑定，要好好珍惜哦！'
    )

# [PUBLIC] `/groupMembers`
groupMembersMatcher = on_command('members')
@groupMembersMatcher.handle()
async def groupMembers(event:GroupMessageEvent, bot:Bot):
    await groupMembersMatcher.finish(
        (await at(event.user_id))+'\n'+
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
async def sign(user:Annotated[User,Depends(require())]):
    if not await stillVaild(user.last_signed_date):
        coins = randint(config.daily_sign_min_coins, config.daily_sign_max_coins)
        user.coins += coins
        user.last_signed_date = datetime.now()
        await updateUser(user)
        await signMatcher.finish(
            (await at(user.id))+
            f'\n签到成功！本次获得{coins}个积分'
        )
    await signMatcher.finish(
        (await at(user.id))+
        "\n本日已签到！请勿重复签到"
    )

# [PUBLIC] `/rank`
rankMatcher = on_command('rank')
@rankMatcher.handle()
async def rank(event:GroupMessageEvent):
    users = await getTop10Users()
    await rankMatcher.finish(
        (await at(event.user_id))+
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
async def refresh(
    user : Annotated[User, Depends(require(0, config.refresh_price))],
    bot : Bot
):
    if couple := await findCouple(user.id, True):
        await rmCouple(couple)
    coupleInfo = await getUserFromId(await couple.opposite(user.id), bot) if couple else None
    await refreshMatcher.finish(
        (await at(user.id))+
        '\n已解除和\n'
        f'{f"{coupleInfo.nick} ({coupleInfo.id})" if coupleInfo else "未绑定或已过期"}\n'
        '的绑定！'
    )

# [SUPER] `/charge`
chargeMatcher = on_command('charge')
@chargeMatcher.handle()
async def charge(
    user : Annotated[User, Depends(require(config.charge_min_perm))],
    arg : Annotated[int, Depends(arg(int))]
):
    user.coins += arg
    await updateUser(user)
    await chargeMatcher.finish(
        (await at(user.id))+
        f'\n已为您的账户充值{arg}积分！'
    )

# [PUBLIC] `/transfer`
transferMatcher = on_command('transfer')
@transferMatcher.handle()
async def transfer(
    user : Annotated[User, Depends(require())],
    mentions : Annotated[List[User], Depends(mentioned(1))],
    arg : Annotated[int, Depends(arg(int))]
):
    if user.coins >= arg:
        mentions[0].coins += arg
        user.coins -= arg
        await updateUser(mentions[0])
        await updateUser(user)
        await transferMatcher.finish(
            (await at(user.id))+
            '\n成功给\n'
            f'{mentions[0].nick} ({mentions[0].id})\n'
            f'转账了{arg}积分！'
        )
    await transferMatcher.finish(
        (await at(user.id))+
        f'积分余额不足以转账{arg}积分！'
    )
