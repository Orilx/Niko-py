from nonebot import on_command, on_notice, plugin
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11 import HonorNotifyEvent
from nonebot.params import CommandArg

from utils.config_util import add_sub_config
from utils.cq_utils import check_role, get_login_info, set_group_ban

__plugin_meta__ = plugin.PluginMetadata(
    name='群管插件',
    description='群组管理相关指令',
    usage=f"""/mute <@某人>  #  禁言指定群员  *管理员指令"""
)

mute = on_command("塞口球", aliases={"mute"}, priority=5, block=True)


@mute.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    bot_qid = (await get_login_info())["user_id"]
    bot_role = await check_role(event.group_id, bot_qid)
    if bot_role != 'admin':
        await mute.finish("请授予Niko管理员权限之后再执行该命令~")

    par = args.extract_plain_text()
    if not par:
        await mute.send('？')

    mute_list = []
    for i in args:
        if i.type == 'at':
            if i.data["qq"] == 'all':
                continue
            else:
                mute_list.append(i.data["qq"])

    if not mute_list:
        await mute.finish('谁？')

    for q_id in mute_list:
        if (await check_role(event.group_id, q_id)) != 'member':
            await mute.send("好像哪里不对劲~")
        else:
            await set_group_ban(event.group_id, q_id, 60)
    await mute.finish('操作完成~')


# member_increase = on_notice(priority=1, block=True)
# member_decrease = on_notice(priority=1)
honor = on_notice(priority=1, block=True)

# mem_notice = add_sub_config('入群欢迎', 'mem_increase_notice')


# @member_increase.handle()
# async def _(event: GroupIncreaseNoticeEvent):
#     if event.group_id not in mem_notice.get_groups():
#         await member_increase.finish()
#     if event.is_tome():
#         await member_increase.finish()
#     await member_increase.send("\n欢迎大佬入群！群地位-1", at_sender=True)
#     if event.operator_id:
#         await member_increase.send(f"由{MessageSegment.at(event.operator_id)}邀请入群")


# @member_decrease.handle()
# async def member_decrease_(event: GroupDecreaseNoticeEvent):
#     id = event.get_user_id()
#     if id == bot.self_id:
#         return
#     # 调用cq的api获取退群人员昵称
#     info = await bot.call_api('get_stranger_info', {
#         'user_id': id
#         })
#     if event.operator_id != id:
#         await member_decrease.finish(f"{info.get('nickname')}({id})\n获赠飞机票一张~")

#     await member_decrease.finish(f"{info.get('nickname')}({id})\n离开了我们")

honor_sub = add_sub_config('龙王提醒', 'honor_sub')


@honor.handle()
async def _(event: HonorNotifyEvent):
    if not honor_sub.get_status():
        await honor.finish()
    if event.group_id not in honor_sub.get_groups():
        await honor.finish()
    dic = {'performer': '群聊之火', 'emotion': '快乐源泉'}
    if event.honor_type != 'talkative':
        await honor.finish(
            f'debug:\nuser_id:{event.user_id}\nhonor_type:{dic.get(event.honor_type)}')
    msg = '恭喜' + MessageSegment.at(event.user_id) + '成为今日龙王~'
    await honor.finish(msg)
