import asyncio
import json
from nonebot.log import logger
from nonebot import on_command, plugin, require
from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         MessageSegment)
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.cq_utils import send_group_msg

from .data_source import format_mblog, get_data, send_mblog_msg
from .data_source import wb_sub_config as wb

__plugin_meta__ = plugin.PluginMetadata(
    name="微博订阅",
    description="微博订阅",
    usage=f"""/查询微博 <微博用户id>  # 查询指定用户最新一条公开微博
/微博订阅 <微博用户id>  # 订阅指定用户微博
/微博订阅列表  # 获取当前群组订阅的所有微博用户
/微博退订 <序号>  # 退订指定序号的微博""",
)

search_wb = on_command("查询微博", priority=5)
add_wb_subscribe = on_command("微博订阅", priority=5, permission=SUPERUSER)
rm_wb_subscribe = on_command("微博退订", priority=5, permission=SUPERUSER)
ls_wb_subscribe = on_command("微博订阅列表", priority=5)

watch = require("nonebot_plugin_apscheduler").scheduler


@watch.scheduled_job("cron", hour="0-7", minute="*/10", jitter=10)
@watch.scheduled_job("cron", hour="8-23", minute="*/2", jitter=10)
async def watch_post():
    # logger.info('开始检查微博更新...')
    for k, v in wb.source_data.items():
        # 跳过订阅群组为空的微博记录
        if not v.get("group_ids"):
            # logger.warning(f'{v.get("screen_name")} skip here!!!!!')
            continue

        mblog = await get_data(k)
        if not mblog:
            logger.warning(f'获取微博失败!')
        else:
            mid = int(mblog["mid"])
            # logger.info(f'检查 {v.get("screen_name")} 微博更新...')
            if mid <= v.get("last"):
                continue

            logger.info(f'检查到 {v.get("screen_name")} 微博更新...')
            # 修改最新bid
            wb.modify_mid(k, mid)

            # 遍历列表发送消息
            for group in v["group_ids"]:
                await asyncio.sleep(5)
                if await send_mblog_msg(group, mblog):
                    logger.success(f'向 {group} 发送：{v.get("screen_name")}')
                else:
                    logger.warning(f'向 {group} 发送：{v.get("screen_name")}失败')
            logger.success("发送完成")


def save_data(uid, dict_remote):
    with open(f"data/{uid}.json", "w", encoding="utf-8") as f:
        json.dump(dict_remote, f, ensure_ascii=False, indent=4)


@search_wb.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        await search_wb.finish("请输入uid~")
    else:
        data = await get_data(par.extract_plain_text())
        await send_mblog_msg(event.group_id, data)


@add_wb_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    msg = "订阅成功："
    if not par:
        await add_wb_subscribe.finish("请输入要订阅微博用户的uid~")
    else:
        uid = par.extract_plain_text()
        post_data = await get_data(par.extract_plain_text())
        name = await wb.add_subscribe(uid, event.group_id, int(post_data.get("mid")))
        if not name:
            await add_wb_subscribe.finish("已经订阅过了~")
        else:
            await add_wb_subscribe.send(msg + name)
            await send_mblog_msg(event.group_id, post_data)


@rm_wb_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    no = par.extract_plain_text()
    if not no:
        # 参数为空
        await add_wb_subscribe.finish("请输入要退订微博用户对应的编号~")
    elif not no.isdigit():
        # 参数不是数字
        await add_wb_subscribe.finish("ERROR: 未知编号")
    else:
        container_list = wb.get_container_list(event.group_id)
        group = event.group_id
        if no not in container_list:
            await add_wb_subscribe.finish("ERROR: 未知编号")
        await wb.rm_subscribe(container_list.get(no), group)
        await add_wb_subscribe.finish("Operation complete.")


@ls_wb_subscribe.handle()
async def _(event: GroupMessageEvent):
    sub_list = wb.group_sub_list(event.group_id)
    msg = "订阅列表："
    num = 0
    for v in sub_list.values():
        msg += f"\n{num}. {v}"
        num += 1
    await ls_wb_subscribe.finish(msg)
