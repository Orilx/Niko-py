from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from plugins import services
from plugins.wb_subscribe.data_source import get_data

add_subscribe = on_command('订阅', priority=5, permission=SUPERUSER)
rm_subscribe = on_command('退订', priority=5, permission=SUPERUSER)
search = on_command('订阅查询', priority=5)

key_words = {'每日课表': services.course_sub_config,
             '龙王提醒': services.honor_sub_config}


@add_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    param = par.extract_plain_text()
    sub = None
    if not param:
        await add_subscribe.finish('你想订阅啥？')
    else:
        if key_words.get(param):
            sub = key_words.get(param)
        else:
            await add_subscribe.finish('咱目前不提供这项服务~')

    if sub.add_group(event.group_id):
        await add_subscribe.finish('订阅成功！')
    else:
        await add_subscribe.finish(f'本群已经订阅过{param}啦~')


@rm_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    param = par.extract_plain_text()
    sub = services.SubConfig('default')
    if not param:
        await add_subscribe.finish('你想退订啥？')
    else:
        if key_words.get(param):
            sub = key_words.get(param)
        else:
            await rm_subscribe.finish('咱目前不提供这项服务~')

    if await sub.rm_group(event.group_id):
        await rm_subscribe.finish('退订成功！')
    await rm_subscribe.finish(f'本群还没订阅{param}呢~')


@search.handle()
async def _(event: GroupMessageEvent):
    msg = '提供的服务：\n(◆表示已订阅)'
    for k, v in key_words.items():
        if v.has_group(event.group_id):
            msg += f'\n◆ {k}'
        else:
            msg += f'\n◇ {k}'
    await search.finish(msg)

