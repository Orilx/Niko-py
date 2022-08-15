import nonebot.adapters.onebot.v11.bot
from nonebot import logger
from nonebot.adapters.onebot.v11 import ActionFailed


async def set_group_ban(g_id, q_id, duration=0):
    await nonebot.get_bot().call_api('set_group_ban', group_id=g_id, user_id=q_id, duration=duration)


async def send_group_msg(g_id: int, msg):
    """
    主动向群组发送消息
    """
    try:
        await nonebot.get_bot().call_api('send_group_msg', group_id=g_id, message=msg)
    except ActionFailed as e:
        logger.warning(f'向{g_id}发送：{str(msg)[:20]}失败,{repr(e)}')
        return False
    else:
        return True


async def send_group_forward_msg(g_id: int, msg):
    """
    发送合并转发 (群)
    """
    try:
        await nonebot.get_bot().call_api('send_group_forward_msg', group_id=g_id, messages=msg)
    except ActionFailed as e:
        logger.warning(f'向{g_id}发送 合并转发 失败,{repr(e)}')
        return False
    else:
        return True


async def get_group_member_info(g_id, q_id):
    """
    获取群成员信息
    """
    info = await nonebot.get_bot().call_api('get_group_member_info', group_id=g_id, user_id=q_id)
    return info


async def get_group_member_list(g_id):
    """
    获取群成员列表
    """
    info = await nonebot.get_bot().call_api('get_group_member_list', group_id=g_id)
    return info


async def check_role(group_id, q_id):
    role = (await get_group_member_info(group_id, q_id))["role"]
    return role


async def get_login_info():
    """
    获取登录号信息
    """
    info = await nonebot.get_bot().call_api('get_login_info')
    return info
