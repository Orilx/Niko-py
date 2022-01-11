import os
import random

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.typing import T_State

from utils.message_builder import image

__plugin_name__ = "来点色图"

setu = on_command('来点色图', priority=5, block=True, aliases= {"GKD"})

IMG_PATH = 'resources/images/setu/'


@setu.handle()
async def setu_(bot: Bot, event: GroupMessageEvent, state: T_State):
    img = random.choice(os.listdir(IMG_PATH))
    await setu.send(image(img, IMG_PATH))
    await setu.finish('您点的一份色图\n喵~', at_sender=True)
