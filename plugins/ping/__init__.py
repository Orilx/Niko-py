from nonebot import on_command

from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment

ping = on_command('ping', priority=5, block=True)

@ping.handle()
async def ping_():
    await ping.finish('pong!')