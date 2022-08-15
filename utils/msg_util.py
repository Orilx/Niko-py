from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment
from utils.cq_utils import get_group_member_info, get_login_info


def poke_cq(id: int) -> "MessageSegment":
    return MessageSegment("poke", {"qq": id})


async def node_custom_cq(qid: int, gid: int, content: list) -> "MessageSegment":
    """
    构造合并转发消息节点
    参见 https://docs.go-cqhttp.org/cqcode/#%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E8%8A%82%E7%82%B9
    """
    nick = await get_group_member_info(gid, qid)

    return MessageSegment("node", {
        "name": "fake_" + (nick["card"] if nick["card"] else nick["nickname"]) + "_仅供娱乐",
        "uin": qid,
        "content": [{"type": i.type, "data": i.data} for i in content]
    })


async def fake_forward_msg(qid: list, gid: int, content: list) -> list:
    """
    构造假合并转发消息
    """
    WARNING_PATH = 'resources/images/warning/'
    bot_qid = (await get_login_info())["user_id"]
    head_msg = [MessageSegment.image(f"file:///{Path(WARNING_PATH + 'fake_msg.png').absolute()}")]
    head = [await node_custom_cq(bot_qid, gid, head_msg)]

    for i in qid:
        head.append(await node_custom_cq(i, gid, content))

    return head
