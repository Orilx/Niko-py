import asyncio
import json

import nonebot
from nonebot import on_command, require, logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment
from plugins.wb_subscribe.data_source import get_data
from .data_source import wb_sub_config as wb

search_wb = on_command('查询微博', priority=5)
add_wb_subscribe = on_command('微博订阅', priority=5, permission=SUPERUSER)
rm_wb_subscribe = on_command('微博退订', priority=5, permission=SUPERUSER)
ls_wb_subscribe = on_command('微博订阅列表', priority=5)

watch = require("nonebot_plugin_apscheduler").scheduler


@watch.scheduled_job("interval", minutes=5, max_instances=5)
# @watch.scheduled_job("interval", seconds=30, max_instances=5)
async def run_every_10_min():
    logger.info('开始检查微博更新...')
    for k, v in wb.source_data.items():
        data_t = await get_data(k)
        bid = int(data_t.get("bid"))
        logger.info(f'检查 {v.get("screen_name")} 微博更新...')
        if bid <= v.get("last"):
            continue
        else:
            # 修改最新bid
            wb.modify_bid(k, bid)
            msg = format_mblog(data_t)
            for group in v.get("group_ids"):
                await asyncio.sleep(5)
                await nonebot.get_bot().call_api('send_group_msg', **{
                    'message': msg,
                    'group_id': group
                })
                logger.success(f'向{group}发送{msg[:10]}')


def save_data(uid, dict_remote):
    with open(f"data/{uid}.json", "w", encoding="utf-8") as f:
        json.dump(dict_remote, f, ensure_ascii=False, indent=4)


def format_mblog(mblog):
    """
    将消息格式化
    """
    msg = MessageSegment.text(f'{mblog["screen_name"]}\n============\n{mblog["text"]}\n')
    for i in mblog.get("images"):
        msg += MessageSegment.image(i) + '\n'
    msg += f'============\n⏰: {mblog["created_at"]}\n🔗: {mblog["url"]}'
    return msg


@search_wb.handle()
async def _(par: Message = CommandArg()):
    if not par:
        await add_wb_subscribe.finish('请输入uid~')
    else:
        data = await get_data(par.extract_plain_text())
        msg = format_mblog(data)
        await add_wb_subscribe.finish(msg)


@add_wb_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    msg = '订阅成功：'
    if not par:
        await add_wb_subscribe.finish('请输入要订阅微博用户的uid~')
    else:
        uid = par.extract_plain_text()
        name = await wb.add_subscribe(uid, event.group_id)
        if not name:
            await add_wb_subscribe.finish('已经订阅过了~')
        else:
            msg += name
        await add_wb_subscribe.send(msg)
        data = await get_data(par.extract_plain_text())
        msg = format_mblog(data)
        await add_wb_subscribe.finish(msg)


@rm_wb_subscribe.handle()
async def _(event: GroupMessageEvent):
    pass


@ls_wb_subscribe.handle()
async def _(event: GroupMessageEvent):
    groups = wb.group_sub_list(event.group_id)
    msg = '订阅列表：'
    for i in groups:
        msg += f'\n- {i}'
    await ls_wb_subscribe.finish(msg)
