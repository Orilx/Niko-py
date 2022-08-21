import asyncio
import datetime

from nonebot import logger, on_command, require, plugin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from utils.config_util import add_sub_config
from utils.cq_utils import send_group_msg
from utils.utils import get_diff_days_2_now
from .data_source import StatusCode, ScheduleManager, ScheduleConfig
from ..weather import Weather

__plugin_meta__ = plugin.PluginMetadata(
    name='课程表',
    description='基于强智 api 实现的课表相关功能',
    usage=f"""/查课表  # 获取今日课表"""
)

course_sub = require("nonebot_plugin_apscheduler").scheduler

week_table = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}


@course_sub.scheduled_job("cron", day_of_week='4', hour='19', minute='35', second='00')
async def update():
    code = await ScheduleManager.refresh_data(True)
    super_group = ScheduleConfig.get_super_group()
    if code.code == 0:
        logger.success("课表定时更新成功")
        for i in super_group:
            await send_group_msg(i, "课表更新成功~")
    else:
        logger.warning("课表定时更新失败")
        for i in super_group:
            await send_group_msg(i, "课表更新失败,请检查日志~")


c_schedule_sub = add_sub_config('每日课表', 'cs_sub')


@course_sub.scheduled_job("cron", day_of_week='0-4', hour='07', minute='10', second='00')
async def run():
    """
    每日定时发送课表
    """
    if not ScheduleConfig.is_begin():
        return
    if not c_schedule_sub.get_status():
        logger.info("每日课表提醒已被关闭")
        return
    # 获取天气
    city = ScheduleConfig.get_location()
    w_daily = await Weather.daily(city)
    data = w_daily['daily'][0]
    weekday = datetime.datetime.now().weekday() + 1
    week = get_diff_days_2_now(ScheduleConfig.get_start_date()) // 7 + 1
    end_day = get_diff_days_2_now(ScheduleConfig.get_end_date())

    msg = f'早上好！\n今天是周{week_table.get(weekday)}，本学期第 {week} 周\n============\n' + ScheduleManager.get_cs_today()
    # 附加天气
    msg += f'\n============\n{city}  日间天气：\n{data["textDay"]}，{data["tempMin"]}~{data["tempMax"]}℃'

    group_id = c_schedule_sub.get_groups()
    for g_id in group_id:
        await asyncio.sleep(5)
        if await send_group_msg(g_id, msg):
            logger.success(f'向 {g_id} 发送课表')
        else:
            logger.warning(f'向 {g_id} 发送课表失败')


cs_select = on_command("查课表", priority=5)
cs_select_week = on_command("本周课表", priority=5)
cs_update = on_command("添加课表", priority=5, permission=SUPERUSER)
cs_delete = on_command("删除课表", priority=5, permission=SUPERUSER)
cs_refresh = on_command("更新课表", priority=5, permission=SUPERUSER)
cs_black_list = on_command("课表黑名单", priority=5, permission=SUPERUSER)


# cs_test = on_command('cs_test', priority=5, permission=SUPERUSER)


@cs_select.handle()
async def _(event: GroupMessageEvent):
    msg = ScheduleManager.get_cs_today()
    await cs_select.finish(msg)


@cs_select_week.handle()
async def _(event: GroupMessageEvent):
    msg = ScheduleManager.get_cs_week()
    await cs_select_week.finish(msg)


@cs_update.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        await cs_update.finish("参数格式:\n课程名称 第几节 教室 开始周次 结束周次\n中间用空格分隔\nEG: 体育与健康 30506 操场 4 13")
    else:
        par_list = par.extract_plain_text().split(' ')
        if len(par_list) != 5:
            await cs_update.finish('参数有误！')
        code = await ScheduleManager.update_data(*par_list)
        await cs_update.finish(code.errmsg)


@cs_delete.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        msg = ScheduleManager.get_sub_table_name_list()
        await cs_delete.finish(msg)
    else:
        param = par.extract_plain_text()
        li = ScheduleManager.get_sub_table_list()
        if not param.isdigit():
            await cs_delete.finish("参数有误~")
        elif int(param) not in range(1, len(li) + 1):
            await cs_delete.finish("参数有误~")
        else:
            code = ScheduleManager.del_data(int(param))
            await cs_delete.finish(code.errmsg)


@cs_refresh.handle()
async def _(event: GroupMessageEvent):
    code = await ScheduleManager.refresh_data()
    await cs_refresh.finish(code.errmsg)


@cs_black_list.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        msg = ScheduleManager.get_black_list()
        if not msg:
            msg = '黑名单为空~'
        await cs_black_list.finish(msg)
    else:
        param = par.extract_plain_text()
        code = ScheduleManager.add_black_list(param)
        await cs_black_list.finish(code.errmsg)
#
#
# @cs_test.handle()
# async def _(event: GroupMessageEvent):
#     await run()
