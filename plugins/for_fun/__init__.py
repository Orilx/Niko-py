import asyncio
import datetime
import json
import os
from pathlib import Path
from random import choice, randint
from re import match

from nonebot import logger, on_command, on_notice, on_regex, require
from nonebot.adapters.onebot.v11 import (GROUP, Bot, GroupMessageEvent,
                                         Message, MessageSegment,
                                         PokeNotifyEvent)
from nonebot.params import CommandArg
from nonebot.rule import to_me
from utils.config_util import SubList, SubManager
from utils.utils import get_json, send_group_msg

from ..weather import Weather

"""
for_fun : 一些实现起来比较简单的指令和定时任务
"""
scheduler = require("nonebot_plugin_apscheduler").scheduler

"""
定时任务
"""

good_night = SubList.add('熄灯提醒', SubManager('night_sub'))


@scheduler.scheduled_job("cron", day_of_week='0-4,6', hour='22', minute='28', second='00')
async def sleep():
    city = '黄岛'
    weather = await Weather.daily(city)
    data = weather['daily'][1]
    msg = f'宿舍即将断电~\n{city}明天天气：{data["textDay"]}，{data["tempMin"]}~{data["tempMax"]}℃'
    group_id = good_night.get_groups()
    for g_id in group_id:
        await asyncio.sleep(5)
        if await send_group_msg(g_id, msg):
            logger.success(f'向 {g_id} 发送熄灯提醒')
        else:
            logger.warning(f'向 {g_id} 发送熄灯提醒失败')


@scheduler.scheduled_job("cron", day_of_week='0-4', hour='08', minute='10', second='00')
async def clock_in():
    group_id = 834474326
    msg = MessageSegment.at(3306007889) + \
          MessageSegment.at(2428444726) + '打卡了没'
    for i in range(randint(1, 5)):
        await asyncio.sleep(1)
        await send_group_msg(group_id, msg)


"""
一些无聊的指令
"""

SETU_PATH = 'resources/images/setu/'  # "色图"存放的地址

ping = on_command('ping', priority=5, block=True)
setu = on_command('来点色图', aliases={"GKD"}, priority=5, block=True)
hitokoto = on_command('一言', priority=5, block=True)
crazy = on_regex(r'疯狂星期\S', permission=GROUP, priority=5, block=True)


@ping.handle()
async def _():
    await ping.finish('pong!')


@setu.handle()
async def _(event: GroupMessageEvent):
    """
    “来点色图”
    """
    msg = MessageSegment.reply(event.message_id) + '您点的一份色图~' + MessageSegment.image(
        f"file:///{Path(SETU_PATH + choice(os.listdir(SETU_PATH))).absolute()}")
    await setu.finish(msg)


@crazy.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """
    “疯狂星期四”
    """
    msg = event.get_plaintext()
    matcher = (match(r'疯狂星期(\S)', msg.replace('天', '日')))
    if not matcher:
        await crazy.finish()
    day = matcher.group(1)
    tb = ['月', '一', '火', '二', '水', '三', '木', '四', '金', '五', '土', '六', '日', '日']
    if day not in tb:
        await crazy.finish()
    idx = int(tb.index(day) / 2) * 2
    # json数据存放路径
    path = Path('resources/text/Thursday.json')
    # 将json对象加载到数组
    with open(path, 'r', encoding='utf-8') as f:
        kfc = json.load(f).get('post')
    # 随机选取数组中的一个对象
    rep = choice(kfc).replace('星期四', '星期' + tb[idx + 1]).replace(
        '周四', '周' + tb[idx + 1]).replace('木曜日', tb[idx] + '曜日')
    await crazy.finish(rep)


@hitokoto.handle()
async def _(par: Message = CommandArg()):
    """
    一言
    """
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
    tb = ['一', '二', '三', '四', '五', '六', '日', '月', '火', '水', '木', '金', '土', '日']
    path = Path('resources/text/Thursday.json')
    # 将json对象加载到数组
    with open(path, 'r', encoding='utf-8') as f:
        kfc = json.load(f).get('post')
    msg = '嗷'
    if randint(0, 101) % 2:
        msg += '~'
    elif randint(0, 101) % 2:
        msg += '呜!'
    else:
        msg += '?'

    if not randint(0, 5):
        msg = '喵~'
    if not randint(0, 10):
        weekday = datetime.datetime.now().weekday()
        msg = choice(kfc).replace('星期四', '星期' + tb[weekday]).replace('周四', '周' + tb[weekday]).replace('木曜日', tb[
            weekday + 7] + '曜日')
    await poke.finish(msg)
