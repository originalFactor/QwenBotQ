from subprocess import run
from pathlib import Path
from os import execl
from sys import executable
from os.path import isdir
from nonebot import get_driver, on_command
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger
from nonebot.permission import SUPERUSER

from . import config
from .bot_utils import strict_to_me


def chk_update():

    rootDir = Path(__file__).parent.parent
    if not isdir(rootDir / ".git"):
        r = run(["git", "init"], cwd=rootDir)
        if r.returncode != 0:
            logger.error("初始化 Git 仓库失败")
            return

    remotes = run(
        ["git", "remote"], cwd=rootDir, capture_output=True, text=True, encoding="utf-8"
    )
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
        ["git", "log", "..sync/dev"],
        cwd=rootDir,
        capture_output=True,
        text=True,
        encoding="utf-8",
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
    execl(executable, executable, Path(__file__).parent.parent / "bot.py")


on_command("update", rule=strict_to_me, permission=SUPERUSER, block=True).handle()(
    chk_update
)


@get_driver().on_startup
async def _():
    scheduler.add_job(chk_update, "interval", hours=24)
    logger.info("QwenBotQ 自动更新已启用！")
