from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from .data_source import search_song, get_song_info

wyy = on_command("点歌", priority=5, block=True)


@wyy.handle()
async def wyy_(event: GroupMessageEvent, param: Message = CommandArg()):
    name = param.extract_plain_text()
    id = ""
    if name:
        id = await search_song(name)
    else:
        await wyy.finish("啥？")
    if not id:
        await wyy.finish("Niko什么也没找到~")
    if id == "e":
        await wyy.finish("Niko遇到了一点小麻烦...请稍后再试！")
    for _ in range(3):
        await wyy.finish(MessageSegment.music("163", id))