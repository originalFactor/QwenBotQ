from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.satori import Bot
from nonebot.adapters.satori.event import PublicMessageEvent

wifeToday = on_command('wife',to_me())
@wifeToday.handle()
def wifeHandler(bot:Bot, event:PublicMessageEvent):
    wifeToday.finish(PublicMessageEvent.json()) # still developing...
