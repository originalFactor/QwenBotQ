from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_reboot import Reloader
from nonebot.log import logger
from nonebot import get_driver
from os.path import isdir
from subprocess import run
from pathlib import Path

from . import config


def chk_update():

    rootDir = Path(__file__).parent.parent
    if not isdir(rootDir / ".git"):
        r = run(["git", "init"], cwd=rootDir)
        if r.returncode != 0:
            logger.error("初始化 Git 仓库失败")
            return

    remotes = run(["git", "remote"], cwd=rootDir, capture_output=True, text=True)
    if remotes.returncode != 0:
        logger.error("获取 Git 远程仓库失败")
        return

    if "sync" not in remotes.stdout:
        r = run(
            [
                "git",
                "remote",
                "add",
                "sync",
                f"{config.github_mirror}https://github.com/OriginalFactor/QwenBotQ.git",
            ],
            cwd=rootDir,
        )
        if r.returncode != 0:
            logger.error("添加 Git 远程仓库失败")
            return

    r = run(["git", "fetch", "sync"], cwd=rootDir)
    if r.returncode != 0:
        logger.error("获取 Git 远程仓库失败")
        return

    status = run(
        ["git", "log", "..sync/dev"], cwd=rootDir, capture_output=True, text=True
    )
    if status.returncode != 0:
        logger.error("获取 Git 状态失败")
        return

    if not status.stdout.strip():
        logger.info("QwenBotQ 已最新")
        return

    r = run(["git", "reset", "--hard", "sync/dev"], cwd=rootDir)
    if r.returncode != 0:
        logger.error("合并 Git 远程仓库失败")
        return

    logger.info("QwenBotQ 已更新")
    Reloader.reload()


@get_driver().on_startup
async def _():
    scheduler.add_job(chk_update, "interval", hours=24)
    logger.info("QwenBotQ 自动更新已启用！")
