from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from .data_source import Weather

current_weather = on_command('当前天气', priority=5, block=True)
today_weather = on_command('天气', priority=5, block=True)


@current_weather.handle()
async def current_weather_(par: Message = CommandArg()):
    if par:
        city = par.extract_plain_text()
        if city == '火星':
            await current_weather.finish('https://mars.nasa.gov/msl/weather/')
        w_now = await Weather.now(city)
        if w_now == -1:
            msg = '神奇的地名'
        elif w_now["code"] == '200':
            data = w_now['now']
            msg = f'{city}  当前天气：\n{data["text"]} {data["temp"]}℃\n{data["windDir"]}，{data["windScale"]}级\n更新时间：{data["obsTime"]}'
        else:
            msg = f'出错了！({w_now["code"]})'
        await current_weather.finish(msg)
    else:
        await current_weather.finish('你想查火星的天气吗？')


@today_weather.handle()
async def today_weather_(par: Message = CommandArg()):
    if par:
        city = par.extract_plain_text()
        if city == '火星':
            await current_weather.finish('https://mars.nasa.gov/msl/weather/')
        w_daily = await Weather.daily(city)
        if w_daily == -1:
            msg = '神奇的地名'
        elif w_daily["code"] == '200':
            data = w_daily['daily'][0]
            msg = f'{city}  日间天气：\n{data["textDay"]}，{data["tempMin"]}~{data["tempMax"]}℃'
        else:
            msg = f'出错了！({w_daily["code"]})'
        await current_weather.finish(msg)
    else:
        await current_weather.finish('你想查火星的天气吗？')
