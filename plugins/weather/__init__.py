from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from data_source import Weather
get_wearther = on_command('天气',priority=5, block=True)

@get_wearther.handle()
async def get_weather_(par: Message = CommandArg()):
        if par:
            city = par.extract_plain_text()
            w = Weather(city_name=city)
            await w.load_data()
            msg = f'{w.now}\n\n{w.daily}'
            await get_wearther.finish(msg)
        else:
            await get_wearther.finish('你想查火星的天气吗？')