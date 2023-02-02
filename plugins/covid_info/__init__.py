from nonebot import get_driver, on_command, require
from nonebot.log import logger
from nonebot.permission import SUPERUSER

from utils.cq_utils import send_group_forward_msg
from .data_source import CovidInfoQindao

super_group = get_driver().config.super_group

# check = on_command("check", priority=5, permission=SUPERUSER)

# watch = require("nonebot_plugin_apscheduler").scheduler


# @check.handle()
# @watch.scheduled_job("cron", minute="*/30", jitter=10)
async def _():
    g_id = CovidInfoQindao.covid_info.get_groups()
    if not (CovidInfoQindao.covid_info.get_status() and g_id):
        return

    info = await CovidInfoQindao.check_update()
    if not info:
        return

    for i in g_id:
        if not await send_group_forward_msg(i, info):
            await CovidInfoQindao.roll_back()
            logger.warning('疫情信息发送失败')
