from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot import on_command, require
import utils.config_util as u_conf
from nonebot.permission import SUPERUSER

add_subcribe = on_command('订阅', priority=5, permission=SUPERUSER)
rm_subcribe = on_command('退订', priority=5,permission=SUPERUSER)
search = on_command('查询', priority=5)

key_words = {'每日课表' : u_conf.course_sub_config,
             '龙王提醒' : u_conf.honor_sub_config}

@add_subcribe.handle()
async def add_subcribe_(event: GroupMessageEvent):
    param = event.get_plaintext()
    sub = None
    if not param:
        await add_subcribe.finish('你想订阅啥？')
    else:
        if key_words.get(param):
            sub = key_words.get(param)
        else:
            await add_subcribe.finish('咱不提供这项服务~')

    if sub.add_group(event.group_id):
        await add_subcribe.finish('订阅成功！')
    else:
        await add_subcribe.finish(f'本群已经订阅过{param}啦~')

@rm_subcribe.handle()
async def rm_subcribe_(event: GroupMessageEvent):
    param = event.get_plaintext()
    sub = None
    if not param:
        await add_subcribe.finish('你想退订啥？')
    else:
        if key_words.get(param):
            sub = key_words.get(param)
        else:
            await rm_subcribe.finish('咱不提供这项服务~')

    if sub.rm_group(event.group_id):
        await rm_subcribe.finish('退订成功！')
    await rm_subcribe.finish(f'本群还没订阅{param}呢~')

@search.handle()
async def search_(event: GroupMessageEvent):
    msg = '提供的服务：\n(前有◆表示已订阅)'
    for k, v in key_words.items():
        if v.has_group(event.group_id):
            msg += f'\n◆ {k}'
        else:
            msg += f'\n◇ {k}'
    await search.finish(msg)
