from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.params import CommandArg

from utils.utils import get_json

hitokoto = on_command('一言', priority=5, block=True)


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