from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
import string
from utils.utils import get_json


bing_img = on_command("bing", priority=5)

@bing_img.handle()
async def bing_img_(bot: Bot, event: MessageEvent, state: T_State):
    if event.get_plaintext():
        await bing_img.finish("这个指令好像不需要参数捏~")
        
    js = get_json("https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1")
    # 遍历列表获得url
    info = ''
    imgUrl = ''
    for item in js.get("images"):
        imgUrl = "https://cn.bing.com" + item.get("url")
        info = item.get("copyright")
    
    # info = info.replace(r"\(([^\)]*)\)","")
    # 不知道为啥replace不生效，暂时用split
    info = info.split(' ')
    msg = MessageSegment.text("今日图片：")+ (MessageSegment.image(imgUrl))+ (f"—— {info[0]}")
    await bing_img.finish(msg)
    
    

