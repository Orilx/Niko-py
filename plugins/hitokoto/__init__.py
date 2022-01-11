from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment
import string
import json
from utils.utils import get_json

hitokoto = on_command('一言')

@hitokoto.handle()
async def hitokoto_(bot: Bot, event: MessageEvent, state: T_State):

    key_word = {'a':'a', 'b':'b', 'c':'c', 'd':'d', 'e':'i', 'wyy': 'j'}
    param = '?c=a&c=b&c=c&c=d&c=i'
    par = event.get_plaintext()
    if par:
        if key_word.get(par):
            param = f'?c={key_word.get(par)}' 
        else:
            await hitokoto.finish('参数有误~')
    
    js = get_json(f'https://v1.hitokoto.cn/{param}')  

    await hitokoto.finish(f"『{js.get('hitokoto')}』\n—— {js.get('from')}")