# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from os import mkdir, remove
from os.path import isdir, isfile
from shutil import rmtree
from typing import Annotated
from uuid import uuid4
import re

from nonebot import on_command
from nonebot.matcher import Matcher
from arclet.alconna import StrMulti
from nonebot_plugin_alconna import (
    Alconna,
    on_alconna,
    Image,
    Args,
    Match,
    Option,
    Arparma,
)
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Bot,
    GroupMessageEvent,
    MessageEvent,
)

from PicImageSearch import EHentai
from ehentaix import EHentaiClient, santize_album_name
from py7zr import SevenZipFile
from httpx import AsyncClient

from .. import config
from ..bot_utils import get_flow_replies, Reply, reply_segment, at_sender
from ..help import Help

Help.append_help("""
【图片搜索】
找本子 [图片] — 以图搜本
下本子 <URL> — 下载本子
搜本子 <关键词> [-l 数量] [-e] — 搜索本子
下一页 — 查看搜索结果下一页（需回复搜索结果）
""")

if not isdir("downloads"):
    mkdir("downloads")


def _safe_filename(name: str, max_len: int = 80) -> str:
    """生成 QQ 群文件可接受的合法文件名。

    QQ 拒绝 `\\ / : * ? " < > |` 及控制字符，统一替换为下划线；
    去除首尾点/空格并截断超长标题，空结果兜底使用随机值。
    """
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f\x7f]', "_", name)
    cleaned = cleaned.strip(" .")[:max_len].rstrip(" .")
    return cleaned or uuid4().hex


def cookies_format(cookies: str):
    return {
        k.strip(): v.strip() for k, v in (c.split("=", 1) for c in cookies.split(";"))
    }


cookies = cookies_format((config.imagesearch.exhentai_cookies or "").strip())


FindBookMatcher = on_alconna(Alconna("找本子", Args["image?", Image]), block=True)


@FindBookMatcher.handle()
async def find_book(image: Match[Image], event: MessageEvent):
    if not image.available:
        await FindBookMatcher.finish("用法：找本子 [图片]", at_sender=at_sender(event))

    ex_cookie = (config.imagesearch.exhentai_cookies or "").strip()

    ehentai = EHentai(is_ex=bool(ex_cookie), cookies=ex_cookie, verify_ssl=False)
    res = await ehentai.search(url=image.result.url)

    if not res.raw:
        await FindBookMatcher.send(
            f"\n{image.result.url}\n没有找到本子", at_sender=at_sender(event)
        )

    for r in res.raw:
        await FindBookMatcher.send(
            "\n" + MessageSegment.image(r.thumbnail) + f"\n{r.title}"
            f"\n{r.type} {r.date}"
            f'\n{" ".join(r.tags)}'
            f"\n{r.url}",
            at_sender=at_sender(event),
        )

    await FindBookMatcher.finish()


DownloadBookMatcher = on_alconna(Alconna("下本子", Args["url?", "url"]), block=True)


@DownloadBookMatcher.handle()
async def download_book(url: Match[str], bot: Bot, event: MessageEvent):
    if not url.available:
        await DownloadBookMatcher.finish(
            "\n用法：下本子 [url]", at_sender=at_sender(event)
        )

    await DownloadBookMatcher.send("\n开始下载...", at_sender=at_sender(event))

    uuid = uuid4().hex

    async with AsyncClient(cookies=cookies) as c:
        ehentai = EHentaiClient(client=c)
        album_name = await ehentai.album(
            url.result,
            f"downloads/{uuid}",
        )

    album_filename = _safe_filename(santize_album_name(album_name))

    await DownloadBookMatcher.send(
        f"\n下载完成：{album_name}\n打包中", at_sender=at_sender(event)
    )

    with SevenZipFile(f"downloads/{uuid}.7z", "w", password=uuid) as archive:
        archive.writeall(f"downloads/{uuid}")

    await DownloadBookMatcher.send(
        f"\n{album_name}打包完成，上传中", at_sender=at_sender(event)
    )

    host = config.fileserver.remote_host
    port = config.fileserver.remote_port or config.fileserver.file_server_port
    file_url = f"http://{host}:{port}/{uuid}.7z"

    try:
        if isinstance(event, GroupMessageEvent):
            await bot.upload_group_file(
                group_id=event.group_id,
                file=file_url,
                name=f"{album_filename}.7z",
            )
        else:
            await bot.upload_private_file(
                user_id=event.user_id,
                file=file_url,
                name=f"{album_filename}.7z",
            )
    except Exception as e:
        await DownloadBookMatcher.finish(
            f"\n上传失败：{e}\n请检查 {file_url} 是否可从 OneBot 端访问",
            at_sender=at_sender(event),
        )
    finally:
        rmtree(f"downloads/{uuid}", ignore_errors=True)
        if isfile(f"downloads/{uuid}.7z"):
            remove(f"downloads/{uuid}.7z")

    await DownloadBookMatcher.finish(
        f"\n{album_name}上传完成\n密码：{uuid}", at_sender=at_sender(event)
    )


async def _send_search_results(
    matcher: Matcher,
    event: MessageEvent,
    query: str,
    limit: int,
    exh: bool,
    msgId: int,
    next: int | None = None,
):
    """发送搜索结果并记录上下文，返回最后一条消息的reply_id"""
    async with AsyncClient(cookies=cookies) as c:
        ehentai = EHentaiClient(client=c)
        res = await ehentai.search(query=query, exhentai=exh, next=next)
        galleries = res.galleries[:limit]
        # 缩略图需带 Cookie 访问，必须在客户端关闭前下载
        thumbs = [await g.thumbnail() for g in galleries]

    if not galleries:
        await matcher.finish("\n没有找到结果", at_sender=at_sender(event))

    reply_id = msgId
    for g, thumb in zip(galleries, thumbs):
        message = reply_segment(reply_id)
        if thumb:
            message += MessageSegment.image(thumb)
        message += f"\n{g.title}"
        message += f"\n{g.type} ⭐{g.rate} {g.published:%Y-%m-%d}"
        message += f'\n{" ".join(g.tags)}'
        message += f"\n{g.url}"
        data = await matcher.send(message, at_sender=at_sender(event))
        reply_id: int = data["message_id"]


search_alconna = Alconna(
    "搜本子",
    Args["query?", StrMulti],
    Option("--limit|-l", Args["limit", int], help_text="展示条目数"),
    Option("--exh|-e", help_text="使用exhentai"),
)
SearchBookMatcher = on_alconna(
    search_alconna,
    block=True,
)


@SearchBookMatcher.handle()
async def search_book(
    query: Match[str], arp: Arparma, event: MessageEvent, matcher: Matcher
):
    if not query.available:
        await SearchBookMatcher.finish(
            "\n用法：搜本子 <关键词> [-l 数量] [-e]", at_sender=at_sender(event)
        )

    limit = arp.query[int]("limit.limit") or 5
    use_exh = arp.find("exh")

    await _send_search_results(
        matcher, event, query.result, limit, use_exh, event.message_id
    )

    await SearchBookMatcher.finish()


NextPageMatcher = on_command("下一页", block=True)


@NextPageMatcher.handle()
async def next_page(
    replies: Annotated[list[Reply] | None, get_flow_replies],
    matcher: Matcher,
    event: MessageEvent,
):
    if not replies:
        await NextPageMatcher.finish(
            "\n用法：[reply] 下一页", at_sender=at_sender(event)
        )

    arp = search_alconna.parse(replies[0].message.extract_plain_text())
    query = arp.query[str]("query")
    last_msg = replies[-1].message.extract_plain_text()
    match = re.search(r"/g/(\d+)/[a-z0-9]+/", last_msg)
    if not match:
        await NextPageMatcher.finish(
            "\n没有找到上一页的结果", at_sender=at_sender(event)
        )

    if not query:
        await NextPageMatcher.finish("\n错误的引用", at_sender=at_sender(event))

    limit = arp.query[int]("limit.limit") or 5
    use_exh = arp.find("exh")

    await _send_search_results(
        matcher=matcher,
        event=event,
        query=query,
        limit=limit,
        next=int(match.group(1)),
        msgId=event.message_id,
        exh=use_exh,
    )

    await NextPageMatcher.finish()
