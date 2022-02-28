import asyncio
import random

from nonebot import get_driver, logger, on_command, on_notice, require
from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         PokeNotifyEvent)
from nonebot.rule import to_me
from utils.utils import send_group_msg
from ..sub_config.services import good_night
from ..weather import Weather

course_sub = require("nonebot_plugin_apscheduler").scheduler


@course_sub.scheduled_job("cron", day_of_week='0-4', hour='22', minute='28', second='00')
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


ping = on_command('ping', priority=5, block=True)


@ping.handle()
async def ping_():
    await ping.finish('pong!')


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
