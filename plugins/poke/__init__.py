from random import randint

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import MessageSegment, PokeNotifyEvent
from nonebot.rule import to_me

from utils.msg_util import poke_cq

poke = on_notice(priority=1, rule=to_me(), block=False)


@poke.handle()
async def _(event: PokeNotifyEvent):
    if not randint(0, 5):
        await poke.send(poke_cq(event.user_id))
    msg = '嗷'
    if randint(0, 101) % 2:
        msg += '~'
    elif randint(0, 101) % 2:
        msg += '呜!'
    else:
        msg += '?'
    if not randint(0, 5):
        msg = MessageSegment.image(
            f"https://bot.orilx.top/pic/cat")
    if not randint(0, 15):
        msg = '呜...'

    await poke.finish(msg)
