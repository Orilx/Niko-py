import os
import time
import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.typing import T_State
from .data_source import get_img

__plugin_name__ = "喜报"

xibao = on_command('喜报', priority=5, block=True)

PATH = 'resources/images/xibao/'

@xibao.handle()
async def xibao_(bot: Bot, event: GroupMessageEvent, state: T_State):
    par = event.get_plaintext()
    if not par:
        await xibao.finish('你的参数呢？')
    if len(par) > 11:
        await xibao.finish('参数太长了~')
    img = await get_img(par)
    msg = MessageSegment.image(img)
    await xibao.finish(msg)