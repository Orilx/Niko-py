from nonebot import on_command, plugin
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.params import CommandArg

from utils.utils import get_json

__plugin_meta__ = plugin.PluginMetadata(
    name='bing 每日一图',
    description='获取 bing 每日一图',
    usage=f"""/bing  # 获取今天的 bing 每日一图"""
)

bing_img = on_command("bing", priority=5, block=True)


@bing_img.handle()
async def bing_img_(param: Message = CommandArg()):
    if param:
        await bing_img.finish("这个指令好像不需要参数捏~")

    js = await get_json("https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1")
    # 遍历列表获得url
    info = ""
    img_url = ""
    for item in js.get("images"):
        img_url = "https://cn.bing.com" + item.get("url")
        info = item.get("copyright")

    # info = info.replace(r"\(([^\)]*)\)","")
    # 不知道为啥replace不生效，暂时用split
    info = info.split(" ")
    msg = (
            MessageSegment.text("今日图片：")
            + (MessageSegment.image(img_url))
            + f"—— {info[0]}"
    )
    await bing_img.finish(msg)
