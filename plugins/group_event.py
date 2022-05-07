from nonebot import on_notice
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, HonorNotifyEvent, \
    MessageSegment
from utils.config_util import SubManager, SubList

member_increase = on_notice(priority=1, block=True)
# member_decrease = on_notice(priority=1)
honor = on_notice(priority=1, block=True)

mem_notice = SubList.add('入群欢迎', SubManager('mem_increase_notice'))


@member_increase.handle()
async def _(event: GroupIncreaseNoticeEvent):
    if event.group_id not in mem_notice.get_groups():
        await member_increase.finish()
    if event.is_tome():
        await member_increase.finish()
    await member_increase.send("\n欢迎大佬入群！群地位-1", at_sender=True)
    if event.operator_id:
        await member_increase.send(f"由{MessageSegment.at(event.operator_id)}邀请入群")


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

honor_sub = SubList.add('龙王提醒', SubManager('honor_sub'))


@honor.handle()
async def honor_(event: HonorNotifyEvent):
    if not honor_sub.get_status():
        await honor.finish()
    if event.group_id not in honor_sub.get_groups():
        await honor.finish()
    dic = {'performer': '群聊之火', 'emotion': '快乐源泉'}
    if event.honor_type != 'talkative':
        await honor.finish(
            f'debug:\nuser_id:{event.user_id}\nhonor_type:{event.honor_type}({dic.get(event.honor_type)})')
    if event.is_tome():
        await honor.finish('啊嘞？龙王竟是我自己！')
    msg = '恭喜' + MessageSegment.at(event.user_id) + '成为今日龙王~'
    await honor.finish(msg)
