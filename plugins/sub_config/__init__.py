from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
from utils.config_util import SubList

add_subscribe = on_command('订阅', priority=5, permission=SUPERUSER)
rm_subscribe = on_command('退订', priority=5, permission=SUPERUSER)
s_manager = on_command('订阅管理', priority=5, permission=SUPERUSER)
search = on_command('订阅查询', priority=5)


@add_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    param = par.extract_plain_text()
    sub = None
    if not param:
        await add_subscribe.finish('你想订阅啥？')
    else:
        if SubList.get(param):
            sub = SubList.get(param)
        else:
            await add_subscribe.finish('咱目前不提供这项服务~')

    if await sub.add_group(event.group_id):
        await add_subscribe.finish('订阅成功！')
    else:
        await add_subscribe.finish(f'本群已经订阅过{param}啦~')


@rm_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    param = par.extract_plain_text()
    sub = None
    if not param:
        await add_subscribe.finish('你想退订啥？')
    else:
        if SubList.get(param):
            sub = SubList.get(param)
        else:
            await rm_subscribe.finish('咱目前不提供这项服务~')

    if await sub.rm_group(event.group_id):
        await rm_subscribe.finish('退订成功！')
    await rm_subscribe.finish(f'本群还没订阅{param}呢~')


@s_manager.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    """
    修改各订阅项目的状态
    本命令影响配置文件中各订阅项目的`enable`字段
    """
    if not par:
        msg = '服务状态 (▲表示已开启)：'
    else:
        param = par.extract_plain_text()
        if SubList.get(param):
            await SubList.get(param).ch_status()
        else:
            await s_manager.finish('咱目前不提供这项服务~')
        msg = '修改成功！\n当前服务状态：'
    li = SubList.get_items()
    for k, v in li.items():
        if v.get_status():
            msg += f'\n▲ {k}'
        else:
            msg += f'\n△ {k}'
    await s_manager.finish(msg)


@search.handle()
async def _(event: GroupMessageEvent):
    li = SubList.get_items()
    msg = '提供的服务 (◆表示已订阅)：'
    for k, v in li.items():
        if v.has_group(event.group_id):
            msg += f'\n◆ {k}'
        else:
            msg += f'\n◇ {k}'
    await search.finish(msg)
