from nonebot import on_command

from nonebot.adapters.onebot.v11 import MessageSegment

help = on_command('帮助', priority=5, block=True)

@help.handle()
async def help_():
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