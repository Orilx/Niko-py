from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot.typing import T_State
import random
poke = on_notice(priority=1, rule=to_me(), block=False)


@poke.handle()
async def poke_(bot: Bot, event: PokeNotifyEvent, state: T_State):
    msg = '喵'
    if random.randint(0, 10):
        msg += '~'
    elif random.randint(0, 5):
        msg += '!'
    else:
        msg += '?'
    if not random.randint(0, 10):
        msg = '嗷！'
    await poke.finish(msg)
