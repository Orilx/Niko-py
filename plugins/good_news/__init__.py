from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment

from .data_source import get_img

__plugin_name__ = "喜报"

xibao = on_command("喜报", priority=5, block=True)

PATH = "resources/images/xibao/"


@xibao.handle()
async def xibao_(event: GroupMessageEvent, param: Message = CommandArg()):
    par = param.extract_plain_text()
    if not par:
        await xibao.finish('你的参数呢？')
    if len(par) > 11:
        await xibao.finish('参数太长了~')
    msg = MessageSegment.image(await get_img(par))
    await xibao.finish(msg)
