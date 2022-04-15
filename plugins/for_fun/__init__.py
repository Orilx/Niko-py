import asyncio
import os
import random
from pathlib import Path

from nonebot import get_driver, logger, on_command, on_notice, plugin, require
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         MessageSegment, PokeNotifyEvent)
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from utils.config_util import SubManager, sub_list
from utils.utils import send_group_msg

from utils.utils import get_json
from ..weather import Weather

"""
for_fun : 一些实现起来比较简单的指令和定时任务
"""
course_sub = require("nonebot_plugin_apscheduler").scheduler

"""
定时任务
"""

good_night = sub_list.add('熄灯提醒', SubManager('night_sub'))


@course_sub.scheduled_job("cron", day_of_week='0-4,6', hour='22', minute='28', second='00')
async def sleep():
    city = '黄岛'
    w = Weather(city)
    await w.load_data()
    data = w.daily['daily'][1]
    msg = f'宿舍即将断电~\n{city}明天天气：{data["textDay"]}，{data["tempMin"]}~{data["tempMax"]}℃'
    group_id = good_night.get_groups()
    for g_id in group_id:
        await asyncio.sleep(5)
        if await send_group_msg(g_id, msg):
            logger.success(f'向 {g_id} 发送熄灯提醒')
        else:
            logger.warning(f'向 {g_id} 发送熄灯提醒失败')


"""
一些无聊的指令
"""

ping = on_command('ping', priority=5, block=True)
# open_door = on_command('芝麻开门', priority=5, block=True)
setu = on_command('来点色图', aliases={"GKD"}, priority=5, block=True)
hitokoto = on_command('一言')


@ping.handle()
async def _():
    await ping.finish('pong!')


IMG_PATH = 'resources/images/setu/'


@setu.handle()
async def setu_(event: GroupMessageEvent):
    ran = random.choice(os.listdir(IMG_PATH))
    img = MessageSegment.image(f"file:///{Path(IMG_PATH + ran).absolute()}")
    await setu.send(img)
    await setu.finish('您点的一份色图\n喵~', at_sender=True)


@hitokoto.handle()
async def hitokoto_(par: Message = CommandArg()):
    key_word = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'i', 'wyy': 'j'}
    param = '?c=a&c=b&c=c&c=d&c=i'
    if par:
        if key_word.get(par.extract_plain_text()):
            param = f'?c={key_word.get(par.extract_plain_text())}'
        else:
            await hitokoto.finish('参数有误~')

    js = await get_json(f'https://v1.hitokoto.cn/{param}')

    await hitokoto.finish(f"『{js.get('hitokoto')}』\n—— {js.get('from')}")


"""
其他
"""

poke = on_notice(priority=1, rule=to_me(), block=False)


@poke.handle()
async def poke_(event: PokeNotifyEvent):
    msg = '嗷'
    if random.randint(0, 5):
        msg += '~'
    elif random.randint(0, 3):
        msg += '!'
    else:
        msg += '?'
    if not random.randint(0, 5):
        msg = '喵~'
    await poke.finish(msg)
