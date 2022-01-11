from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment

help = on_command('帮助', priority=5)

@help.handle()
async def help_(bot: Bot, event: MessageEvent, state: T_State):
    msg ='''Niko还在学习新的功能~
目前支持的功能：
* /喜报
* /一言
* /点歌
* /每日龙王提醒
* /来点色图
* /bing
* /ping'''
    await help.finish(msg)