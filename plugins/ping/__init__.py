from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment

help = on_command('ping', priority=5)

@help.handle()
async def help_(bot: Bot, event: MessageEvent, state: T_State):
    await help.finish('pong!')