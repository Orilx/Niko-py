import nonebot
from nonebot import get_driver
from nonebot import on_command

from nonebot.adapters.onebot.v11 import GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER

# mute = on_command("mute", priority=5, block=True, permission=GROUP_ADMIN|GROUP_OWNER)

# @mute.got("member", prompt="谁？")
# async def mute_(event: GroupMessageEvent):
#     member = state["member"].replace('[CQ:at,qq=','').replace(']','')
    
#     await bot.call_api('set_group_ban', **{
#         'group_id': event.group_id,
#         'user_id': member,
#         'duration': 60*60
#         })
#     await mute.finish('finished')