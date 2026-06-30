# Copyright (c) 2026 originalFactor
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from aiohttp import web
from nonebot import get_driver
from os.path import isdir
from os import mkdir
from .. import config

__all__ = []


def create_app() -> web.Application:
    app = web.Application()
    if not isdir("downloads"):
        mkdir("downloads")
    app.router.add_static("/", "downloads")
    return app


runner = web.AppRunner(create_app())


@get_driver().on_startup
async def _start():
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.imagesearch.file_server_port)
    await site.start()


@get_driver().on_shutdown
async def _stop():
    await runner.cleanup()
