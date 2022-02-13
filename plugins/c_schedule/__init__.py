import asyncio
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot import on_command, require, logger
from nonebot.params import CommandArg

from plugins.sub_config.services import c_schedule_sub
from utils.utils import send_group_msg
from .data_source import cs_manager

course_sub = require("nonebot_plugin_apscheduler").scheduler

time_table = {'0102': '一', '0304': '二', '0506': '三', '0708': '四', '0910': '五'}
week_table = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '日'}


@course_sub.scheduled_job("cron", day_of_week='0-4', hour='07', minute='00', second='00')
async def run():
    """
    每日定时发送课表
    """
    if not c_schedule_sub.get_status():
        logger.info("每日课表提醒已被关闭")
        return
    group_id = c_schedule_sub.get_groups()
    msg = '早上好！\n'
    for g_id in group_id:
        await asyncio.sleep(5)
        if await send_group_msg(g_id, msg):
            logger.success(f'向 {g_id} 发送今日课表')
        else:
            logger.warning(f'向 {g_id} 发送课表失败')


cs_select = on_command("查课表", priority=5)
cs_update = on_command("修改课表", priority=5)
cs_refresh = on_command("更新课表", priority=5)


@cs_select.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    msg = '今日课表'
    if not par:
        data = cs_manager.get_cs_today()
        if not data:
            msg = '今天没有课哦~'
        else:
            for k, v in data.items():
                msg += f'\n第{time_table.get(k[1:5])}节  {v.get("c_name")}, {v.get("c_room")}'
    else:
        args = par.extract_plain_text()
    await cs_select.finish(msg)


@cs_update.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    pass


@cs_refresh.handle()
async def _(event: GroupMessageEvent):
    cs_manager.update_data()
    await cs_refresh.finish("更新完成！")
