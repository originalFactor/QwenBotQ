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

from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union
from urllib.error import HTTPError
from asyncio import sleep
from datetime import datetime, timedelta
from aiohttp import ClientSession
from nonebot import get_driver, get_bot
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_apscheduler import scheduler
from . import config
from .database import SubscribeStatus

FEED_TEMPLATE = \
'您关注的UP主 {uploader} 更新了一条动态：\n'\
'{content}'

LIVE_TEMPLATE = \
'您关注的UP主 {uploader} 正在直播：\n'\
'{content}'

class NoticeType(str, Enum):
    '提醒类型'
    FEED = 'feed'
    LIVE = 'live'

async def notice(
    event: str,
    name: str,
    tp: NoticeType,
    users: Sequence[str],
    groups: Sequence[str]
    ):
    '消息提醒'
    bot: Bot = get_bot()
    message = (FEED_TEMPLATE if tp==NoticeType.FEED else LIVE_TEMPLATE).format(
        uploader = name,
        content = event
    )
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

async def save_debug(content: bytes):
    with open('dbg_apiresult.json', 'wb') as f:
        f.write(content)

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
            await save_debug(await resp.read())
            response = await resp.json()
    except HTTPError as e:
        logger.error(f'Network error during requesting bilibili: {e}')
        return None
    if response['code'] != 0:
        logger.error(f'API returned error: {response["message"]}')
        return None
    return response

async def check_and_push(session: ClientSession):
    '定期检查并推送动态及直播'
    logger.info("动态和直播推送开始检查……")
    for focus in config.focus.subscribes:
        if not (status := await SubscribeStatus.get(focus.uid)):
            status = SubscribeStatus(id=focus.uid)
            await status.save()
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
                if item['id_str'] == status.last_update:
                    has_more = False
                    break
                if desc := item['modules']['module_dynamic']['desc']:
                    await notice(
                        desc['text'],
                        item['modules']['module_author']['name'],
                        'feed',
                        focus.users,
                        focus.groups
                    )
            await sleep(5)
        await status.set({SubscribeStatus.last_update: last_update})
        this_page = 1
        total_page = 1
        while this_page <= total_page:
            if not (response := await api_request(
                session,
                'https://api.live.bilibili.com/xlive/web-ucenter/user/following',
                {
                    'page': this_page,
                    'ignore_record': 1,
                    'hit_ab': 1
                }
            )):
                break
            data = response['data']
            total_page = data['totalPage']
            this_page += 1
            finded = False
            for room in data['list']:
                if room['uid'] == focus.uid:
                    if room['live_status'] and not status.living:
                        await notice(
                            room['title'],
                            room['uname'],
                            'live',
                            focus.users,
                            focus.groups
                        )
                    await status.set({SubscribeStatus.living: bool(room['live_status'])})
                    finded = True
                    break
            if finded:
                break
            await sleep(5)
        await sleep(5)
    logger.info("动态和直播推送检查完毕")

pool: List[ClientSession] = []

@get_driver().on_startup
async def on_startup():
    '注册计划任务'
    if config.focus:
        pool.append(ClientSession(
            cookies={'SESSDATA': config.focus.sessdata},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0'}
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
    await pool[-1].close()
