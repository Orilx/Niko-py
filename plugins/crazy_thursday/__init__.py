import json
from pathlib import Path
from random import choice
from re import match

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent

crazy = on_regex(r'疯狂星期\S', permission=GROUP, priority=5, block=True)


def get_crazy(idx: int):
    tb = ['一', '二', '三', '四', '五', '六', '日', '月', '火', '水', '木', '金', '土', '日']
    # json数据存放路径
    path = Path('resources/text/Thursday.json')
    # 将json对象加载到数组
    with open(path, 'r', encoding='utf-8') as f:
        kfc = json.load(f).get('post')
    # 随机选取数组中的一个对象
    rep = choice(kfc).replace('星期四', '星期' + tb[idx]).replace(
        '周四', '周' + tb[idx]).replace('木曜日', tb[idx + 7] + '曜日')
    return rep


@crazy.handle()
async def _(event: GroupMessageEvent):
    """
    “疯狂星期四”
    """
    msg = event.get_plaintext()
    matcher = (match(r'疯狂星期(\S)', msg.replace('天', '日')))
    if not matcher:
        await crazy.finish()
    day = matcher.group(1)
    print(day)
    tb = ['一', '二', '三', '四', '五', '六', '日']
    if day not in tb:
        await crazy.finish()
    idx = tb.index(day)
    await crazy.finish(get_crazy(idx))

