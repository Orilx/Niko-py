from nonebot import on_command, plugin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg


from .data_source import search_song, get_song_info

__plugin_meta__ = plugin.PluginMetadata(
    name='点歌',
    description='点歌',
    usage=f"""/点歌 <歌名>  # 点歌"""
)

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