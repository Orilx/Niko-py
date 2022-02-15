from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import PokeNotifyEvent
import random
poke = on_notice(priority=1, rule=to_me(), block=False)


@poke.handle()
async def poke_(event: PokeNotifyEvent):
    msg = '嗷'
    if random.randint(0, 5):
        msg += '~'
    elif random.randint(0, 3):
        msg += '!'
    else:
        msg += '?'
    if not random.randint(0,5):
        msg = '喵~'
    await poke.finish(msg)
