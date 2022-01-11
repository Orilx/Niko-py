import nonebot
from nonebot import get_driver
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER

# mute = on_command("mute", priority=5, permission=GROUP_ADMIN|GROUP_OWNER)

# @mute.got("member", prompt="谁？")
# async def mute_(bot: Bot, event: GroupMessageEvent, state: T_State):
#     member = state["member"].replace('[CQ:at,qq=','').replace(']','')
    
#     await bot.call_api('set_group_ban', **{
#         'group_id': event.group_id,
#         'user_id': member,
#         'duration': 60*60
#         })
#     await mute.finish('finished')