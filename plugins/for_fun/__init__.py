from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

"""
for_fun : 一些实现起来比较简单的指令
"""
ping = on_command('ping', priority=5, block=True)
setu = on_command('来点色图', aliases={"GKD"}, priority=5, block=True)


@ping.handle()
async def _():
    await ping.finish('pong!')


@setu.handle()
async def _(event: GroupMessageEvent):
    """
    “来点色图”
    """
    msg = MessageSegment.reply(event.message_id) + '您点的一份色图~' + MessageSegment.image("https://bot.orilx.top/pic/cat")
    await setu.finish(msg)
