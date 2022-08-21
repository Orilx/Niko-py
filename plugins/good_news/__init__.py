from pathlib import Path

from nonebot import on_command, plugin
from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         MessageSegment)
from nonebot.params import CommandArg
from nonebot_plugin_htmlrender import get_new_page

__plugin_meta__ = plugin.PluginMetadata(
    name='喜报',
    description='生成喜报',
    usage=f"""/喜报 <参数>  # 生成一张喜报"""
)

xibao = on_command("喜报", priority=5, block=True)

PATH = Path('resources/html/xibao.html').absolute()


@xibao.handle()
async def _(event: GroupMessageEvent, param: Message = CommandArg()):
    par = param.extract_plain_text()
    if not par:
        await xibao.finish('你的参数在哪！让它上前来！')
    if len(par) > 11:
        await xibao.finish('参数太长了~')
    async with get_new_page(viewport={"width": 600, "height": 430}) as page:
        await page.goto(
            f"file://{PATH}?text={par}",
            wait_until="networkidle",
        )
        pic = await page.screenshot(full_page=True)
    await xibao.finish(MessageSegment.image(pic))
