import asyncio
import json

import nonebot
from nonebot import on_command, require, logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, MessageSegment, exception
from plugins.wb_subscribe.data_source import get_data
from .data_source import wb_sub_config as wb
from utils.utils import send_group_msg

search_wb = on_command('查询微博', priority=5)
add_wb_subscribe = on_command('微博订阅', priority=5, permission=SUPERUSER)
rm_wb_subscribe = on_command('微博退订', priority=5, permission=SUPERUSER)
ls_wb_subscribe = on_command('微博订阅列表', priority=5)

watch = require("nonebot_plugin_apscheduler").scheduler


@watch.scheduled_job("cron", hour='22-23,0-7', minute='*/10', jitter=10)
@watch.scheduled_job("cron", hour='8-21', minute='*/2', jitter=10)
# @watch.scheduled_job("interval", seconds=30)
async def watch_post():
    # logger.info('开始检查微博更新...')
    for k, v in wb.source_data.items():
        data_t = await get_data(k)
        # 跳过订阅群组为空的微博记录
        if not v.get("group_ids"):
            # logger.warning(f'{v.get("screen_name")} skip here!!!!!')
            continue
        bid = int(data_t.get("bid"))
        # logger.info(f'检查 {v.get("screen_name")} 微博更新...')
        if bid <= v.get("last"):
            continue
        else:
            logger.info(f'检查到 {v.get("screen_name")} 微博更新...')
            # 修改最新bid
            wb.modify_bid(k, bid)
            msg = format_mblog(data_t)
            for group in v.get("group_ids"):
                await asyncio.sleep(5)
                if await send_group_msg(group, msg):
                    logger.success(f'向 {group} 发送：{v.get("screen_name")}')
                else:
                    logger.warning(f'向 {group} 发送：{v.get("screen_name")}失败')


def save_data(uid, dict_remote):
    with open(f"data/{uid}.json", "w", encoding="utf-8") as f:
        json.dump(dict_remote, f, ensure_ascii=False, indent=4)


def format_mblog(mblog):
    """
    将消息格式化
    """
    if not mblog.get("bid"):
        return '该账号暂无最新微博~'
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
        data = await get_data(par.extract_plain_text())
        name = await wb.add_subscribe(uid, event.group_id, int(data.get("bid")))
        if not name:
            await add_wb_subscribe.finish('已经订阅过了~')
        else:
            await add_wb_subscribe.send(msg + name)
            await add_wb_subscribe.finish(format_mblog(data))


@rm_wb_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    no = par.extract_plain_text()
    if not no:
        # 参数为空
        await add_wb_subscribe.finish('请输入要退订微博用户对应的编号~')
    elif not no.isdigit():
        # 参数不是数字
        await add_wb_subscribe.finish('ERROR: 未知编号')
    else:
        container_list = wb.get_container_list(event.group_id)
        group = event.group_id
        if no not in container_list:
            await add_wb_subscribe.finish('ERROR: 未知编号')
        await wb.rm_subscribe(container_list.get(no), group)
        await add_wb_subscribe.finish('Operation complete.')


@ls_wb_subscribe.handle()
async def _(event: GroupMessageEvent):
    sub_list = wb.group_sub_list(event.group_id)
    msg = '订阅列表：'
    num = 0
    for k, v in sub_list.items():
        msg += f'\n{num}. {v}'
        num += 1
    await ls_wb_subscribe.finish(msg)
