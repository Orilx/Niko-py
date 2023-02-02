from nonebot import on_command, plugin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler

from .data_source import WbSubConfig
from .data_source import check_update, get_latest_item, send_mblog

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
check = on_command("check_wb", priority=5, permission=SUPERUSER)


@scheduler.scheduled_job("cron", hour="0-7", minute="*/10", jitter=10)
@scheduler.scheduled_job("cron", hour="8-23", minute="*/2", jitter=10)
@check.handle()
async def watch_post():
    await check_update()


@search_wb.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        await search_wb.finish("请输入uid~")
    else:
        uid = par.extract_plain_text()
        if not str.isdigit(uid):
            await search_wb.finish("uid 不合法")

        uid = int(uid)
        await send_mblog(event.group_id, await get_latest_item(uid))


@add_wb_subscribe.handle()
async def _(event: GroupMessageEvent, par: Message = CommandArg()):
    if not par:
        await add_wb_subscribe.finish("请输入要订阅微博用户的uid~")
    else:
        uid = par.extract_plain_text()
        if not str.isdigit(uid):
            await search_wb.finish("uid 不合法")
        uid = int(uid)

        post_data = await get_latest_item(uid)
        name = await WbSubConfig.add_subscribe(uid, event.group_id, post_data["mid"])
        if not name:
            await add_wb_subscribe.finish("已经订阅过了~")
        else:
            await add_wb_subscribe.send(f"订阅成功：{name}")
            await send_mblog(event.group_id, post_data)


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
        container_list = WbSubConfig.get_container_list(event.group_id)
        group = event.group_id
        if no not in container_list:
            await add_wb_subscribe.finish("ERROR: 未知编号")
        await WbSubConfig.rm_subscribe(container_list[no], group)
        await add_wb_subscribe.finish("Operation complete.")


@ls_wb_subscribe.handle()
async def _(event: GroupMessageEvent):
    sub_list = WbSubConfig.group_sub_list(event.group_id)
    msg = "订阅列表："
    num = 0
    for v in sub_list.values():
        msg += f"\n{num}. {v}"
        num += 1
    await ls_wb_subscribe.finish(msg)
