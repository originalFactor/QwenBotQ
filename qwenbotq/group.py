# Copyright (C) 2024 OriginalFactor
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

'群组相关功能'

from random import choice
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.adapters.onebot.v11.event import Reply
from .models import EssenceMessage


MembersMatcher = on_command('群友列表', block=True)

@MembersMatcher.handle()
async def group_members(event: GroupMessageEvent, bot: Bot):
    '群友列表'
    await MembersMatcher.finish(
        '\n' +
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
        ),
        at_sender=True
    )


RandomEssenceMatcher = on_command('掏精', block=True)

@RandomEssenceMatcher.handle()
async def random_essence(event: GroupMessageEvent, bot: Bot):
    '获取随机群精华'
    essence = EssenceMessage.model_validate(
        choice(
            await bot.get_essence_msg_list(group_id=event.group_id)
        )
    )
    msg = Reply.model_validate(await bot.get_msg(message_id=essence.message_id))
    await RandomEssenceMatcher.finish(
        f'\n{essence.sender_nick} ({essence.sender_id})\n'
        f'{essence.sender_time.strftime("%Y/%m/%d %H:$M:%S")}：\n\t'+
        msg+
        f'\n由 {essence.operator_nick} ({essence.operator_id}) 于\n\t'
        f'{essence.operator_time} 设置。',
        at_sender=True
    )
