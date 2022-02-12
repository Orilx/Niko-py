import os
import random
from pathlib import Path
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment

setu = on_command('来点色图', aliases={"GKD"}, priority=5, block=True)

IMG_PATH = 'resources/images/setu/'


@setu.handle()
async def setu_(event: GroupMessageEvent):
    ran = random.choice(os.listdir(IMG_PATH))
    img = MessageSegment.image(f"file:///{Path(IMG_PATH + ran).absolute()}")
    await setu.send(img)
    await setu.finish('您点的一份色图\n喵~', at_sender=True)
