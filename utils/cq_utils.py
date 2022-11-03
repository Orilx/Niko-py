import nonebot
from nonebot.adapters.onebot.v11 import ActionFailed, MessageSegment
from nonebot.log import logger

from utils.msg_util import NodeMsg, NodeMsgList


async def set_group_ban(g_id: int, q_id: int, duration=0):
    """
    设置禁言
    """
    await nonebot.get_bot().call_api(
        "set_group_ban", group_id=g_id, user_id=q_id, duration=duration
    )


async def send_group_msg(g_id: int, msg):
    """
    主动向群组发送消息
    """
    try:
        await nonebot.get_bot().call_api("send_group_msg", group_id=g_id, message=msg)
    except ActionFailed as e:
        logger.warning(f"向{g_id}发送：{str(msg)[:20]}失败,{repr(e)}")
        return False
    else:
        return True


async def get_group_member_info(g_id, q_id):
    """
    获取群成员信息
    """
    info = await nonebot.get_bot().call_api(
        "get_group_member_info", group_id=g_id, user_id=q_id
    )
    return info


async def get_group_member_list(g_id):
    """
    获取群成员列表
    """
    info = await nonebot.get_bot().call_api("get_group_member_list", group_id=g_id)
    return info


async def check_role(group_id, q_id):
    role = (await get_group_member_info(group_id, q_id))["role"]
    return role


async def get_login_info():
    """
    获取登录号信息
    """
    info = await nonebot.get_bot().call_api("get_login_info")
    return info


async def construct_forward_msg(gid: int, node: NodeMsg) -> MessageSegment:
    """
    处理合并转发消息节点
    参见 https://docs.go-cqhttp.org/cqcode/#%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E8%8A%82%E7%82%B9
    """
    if not node.nick_name:
        info = await get_group_member_info(gid, node.qid)
        node.nick_name = info["card"] if info["card"] else info["nickname"]

    return MessageSegment(
        "node",
        {
            "name": node.nick_name,
            "uin": node.qid,
            "content": [{"type": i.type, "data": i.data} for i in node.msg],
        },
    )


async def send_group_forward_msg(g_id: int, msg: NodeMsgList):
    """
    发送合并转发 (群)
    """
    forward_msg = [await construct_forward_msg(g_id, i) for i in msg.get()]
    try:
        await nonebot.get_bot().call_api(
            "send_group_forward_msg", group_id=g_id, messages=forward_msg
        )
    except ActionFailed as e:
        logger.warning(f"向{g_id}发送 合并转发 失败,{repr(e)}")
        return False
    else:
        return True
