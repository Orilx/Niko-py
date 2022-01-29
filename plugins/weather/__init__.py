from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .data_source import Weather

current_wearther = on_command('当前天气', priority=5, block=True)
today_wearther = on_command('天气', priority=5, block=True)


@current_wearther.handle()
async def current_weather_(par: Message = CommandArg()):
    if par:
        city = par.extract_plain_text()
        w = Weather(city)
        await w.load_data()
        msg = ''
        if w.city_id == -1:
            msg = '神奇的地名'
        elif w.now["code"] == '200':
            data = w.now['now']
            msg = f'{city}  当前天气：\n{data["text"]}\n当前温度：{data["temp"]}℃\n{data["windDir"]}，{data["windScale"]}级\n更新时间：{data["obsTime"]}'
        else:
            msg = f'出错了！({w.now["code"]})'
        await current_wearther.finish(msg)
    else:
        await current_wearther.finish('你想查火星的天气吗？')


@today_wearther.handle()
async def today_weather_(par: Message = CommandArg()):
    if par:
        city = par.extract_plain_text()
        w = Weather(city)
        await w.load_data()
        msg = ''
        if w.city_id == -1:
            msg = '神奇的地名'
        elif w.daily["code"] == '200':
            data = w.daily['daily'][0]
            msg = f'{city}  日间天气：\n{data["textDay"]}，{data["tempMin"]}~{data["tempMax"]}℃\n{data["windDirDay"]}，{data["windSpeedDay"]}级'
        else:
            msg = f'出错了！({w.daily["code"]})'
        await current_wearther.finish(msg)
    else:
        await current_wearther.finish('你想查火星的天气吗？')
