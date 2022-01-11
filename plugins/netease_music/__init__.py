from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from .data_source import search_song

wyy = on_command('点歌', priority=5)

@wyy.handle()
async def wyy_(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state['name'] = args

@wyy.got('name', prompt='你想搜什么？')
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    name = state['name']
    id = await search_song(name)
    if not id:
        await wyy.finish('Niko什么也没找到~')
    for _ in range(3):
        song_content = [{"type": "music", "data": {"type": 163, "id": id}}]
        await wyy.finish(song_content)
    else:
        await wyy.finish("Niko遇到了一点小麻烦...")
