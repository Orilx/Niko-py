from nonebot import get_driver
from nonebot import on_command, plugin
from nonebot.adapters.onebot.v11 import Message, Event, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

help_doc = on_command('帮助', priority=3, block=True, aliases={"help"})
plugin_list = on_command('功能列表', priority=5, block=True)

__plugin_meta__ = plugin.PluginMetadata(
    name='帮助文档',
    description='获取Niko目前可用的所有功能',
    usage=f"""Niko还在学习新的功能~
/功能列表  # 展示已加载插件列表
/帮助 <插件名称>  # 调取目标插件帮助信息"""
)

driver = get_driver()

plugin_doc_list = {}


@driver.on_startup
async def load_plugin_info():
    plugin_set = plugin.get_loaded_plugins()
    global plugin_doc_list
    for p in plugin_set:
        if p.metadata:
            plugin_doc_list[p.metadata.name] = p


@help_doc.handle()
async def _(event: Event, matcher: Matcher, args: Message = CommandArg()):
    arg = args.extract_plain_text().strip()

    if not args:
        msg = f'{__plugin_meta__.name}\n================\n{__plugin_meta__.usage}'
        await help_doc.finish(msg)

    if arg not in plugin_doc_list.keys():
        msg = f'[{arg}] 不存在或未加载，请确认输入了正确的插件名'
    else:
        p = plugin_doc_list.get(arg)

        msg = f'{p.metadata.name}\n================\n{p.metadata.usage}'

    await help_doc.finish(msg)


@plugin_list.handle()
async def _(event: GroupMessageEvent):
    msg = '功能列表：'
    for i in plugin_doc_list.values():
        msg += f"\n- {i.metadata.name} | {i.metadata.description}"

    await plugin_list.finish(msg)




