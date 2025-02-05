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

'BiliBili动态提醒服务'

from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from urllib.error import HTTPError
from asyncio import sleep
from datetime import datetime, timedelta
from aiohttp import ClientSession
from nonebot import get_driver, get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment
from nonebot_plugin_apscheduler import scheduler
from . import config
from .database import SubscribeStatus

async def notice(
    message: Union[str, Message],
    users: Sequence[str],
    groups: Sequence[str]
    ):
    '消息提醒'
    bot: Bot = get_bot()
    for user in users:
        await bot.send_msg(
            user_id = int(user),
            message = message
        )
    for group in groups:
        await bot.send_msg(
            group_id = int(group),
            message = message
        )

async def api_request(
        session: ClientSession,
        endpoint: str,
        params: Mapping[str, Union[str, int, float]]
    ) -> Optional[Dict[str, Any]]:
    '请求API接口'
    try:
        async with session.get(
            endpoint,
            params=params
        ) as resp:
            if resp.status != HTTPStatus.OK:
                logger.error(f'Server returned an invalid HTTP status code: {resp.status}')
                return None
            logger.debug(f'API returned result: {await resp.text()}')
            response = await resp.json()
    except HTTPError as e:
        logger.error(f'Network error during requesting bilibili: {e}')
        return None
    if response['code'] != 0:
        logger.error(f'API returned error: {response["message"]}')
        return None
    return response

async def parse_item(item: Mapping[str, Any]) -> Optional[Union[str, Message]]:
    '渲染动态'
    _type = item['type']
    module = item['modules']
    dynamic = module['module_dynamic']
    desc = dynamic['desc']
    major = dynamic['major']

    head = f'您关注的UP主 {module["module_author"]["name"]} '
    if _type == 'DYNAMIC_TYPE_FORWARD':
        if _ := await parse_item(item['orig']):
            return head+'转发了一条动态：\n'+_
    elif _type == 'DYNAMIC_TYPE_AV':
        archive = major['archive']
        return head+'投稿了一条视频：'+\
            MessageSegment.image(archive['cover'])+\
            f'{archive["title"]}\n'\
            f'https:{archive["jump_url"]}'
    elif _type == 'DYNAMIC_TYPE_WORD':
        return head+f'发表了一条动态：\n{desc["text"]}'
    elif _type == 'DYNAMIC_TYPE_DRAW':
        r = head+f'发表了一条动态：\n{desc["text"]}'
        for img in major['draw']['items']:
            r += MessageSegment.image(img['src'])
        return r
    elif _type == 'DYNAMIC_TYPE_ARTICLE':
        article = major['article']
        r = head+f'发表了一篇专栏：\n{article["title"]}\n{article["jump_url"]}'
        for cover in article['covers']:
            r += MessageSegment.image(cover)
        return r
    logger.warning(f'请求进行未实现的 {_type} 类型动态渲染')
    return None

async def check_and_push(session: ClientSession):
    '定期检查并推送动态及直播'
    logger.info("动态和直播推送开始检查……")
    for focus in config.focus.subscribes:
        logger.info(f'正在检查 {focus.uid}')
        if not (status := await SubscribeStatus.get(focus.uid)):
            status = SubscribeStatus(id=focus.uid)
            await status.save()
        logger.info('正在检查动态')
        offset = ''
        has_more = True
        last_update = ''
        while has_more:
            if not (response := await api_request(
                session,
                'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all',
                {
                    'host_mid': focus.uid,
                    'offset': offset
                }
            )):
                break
            data = response['data']
            has_more = data['has_more']
            if not data['items']:
                logger.info('无数据可用')
                break
            if last_update == '':
                last_update = data['items'][0]['id_str']
            offset = data['offset']
            for item in data['items']:
                if int(item['id_str']) <= status.last_update:
                    has_more = False
                    break
                if _ := await parse_item(item):
                    logger.info(f'找到一条新动态：\n{_}')
                    await notice(
                        _,
                        focus.users,
                        focus.groups
                    )
            await sleep(3)
        if last_update:
            await status.set({SubscribeStatus.last_update: int(last_update)})
        logger.info(f'动态检查完毕，最后一条动态的id：{last_update}')
        logger.info('开始检查直播')
        if response := await api_request(
            session,
            'https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids',
            {'uids[]': [focus.uid]}
        ):
            data = response['data'][focus.uid]
            if data['live_status'] and not status.living:
                logger.info(f'用户正在直播，标题：{data["title"]}')
                await notice(
                    f'您关注的UP主 {data["uname"]} 正在直播：\n'
                    f'{data["title"]}'+
                    MessageSegment.image(data['cover_from_user'])+
                    f'开播时间：{datetime.fromtimestamp(data["live_time"]).strftime("%Y/%m/%d %H:%M:%S")}',
                    focus.users,
                    focus.groups
                )
            elif not data['live_status'] and status.living:
                logger.info(f'用户停止直播')
            await status.set({SubscribeStatus.living: bool(data['live_status'])})
        logger.info('直播检查完毕')
        await sleep(3)
    logger.info("动态和直播推送检查完毕")

pool: List[ClientSession] = []

@get_driver().on_startup
async def on_startup():
    '注册计划任务'
    if config.focus:
        pool.append(ClientSession(
            cookies={'SESSDATA': config.focus.sessdata},
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) '
                    'Gecko/20100101 Firefox/132.0'
            }
        ))
        logger.info(f'注册了计划任务，参数 {config.focus.interval}')
        scheduler.add_job(
            check_and_push,
            'interval',
            kwargs={'session': pool[-1]},
            start_date=datetime.now()+timedelta(minutes=1),
            **config.focus.interval
        )

@get_driver().on_shutdown
async def on_shutdown():
    '关闭客户端session'
    for session in pool:
        await session.close()
