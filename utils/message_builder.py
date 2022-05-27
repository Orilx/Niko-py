from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment, Message
from utils.utils import get_group_member_info, get_login_info


def poke_cq(id: int) -> "MessageSegment":
    return MessageSegment("poke", {"qq": id})


async def fake_node_msg(qid: list, gid: int, content: list):
    """
    构造假合并转发消息
    """
    WARNING_PATH = 'resources/images/warning/'
    bot_qid = (await get_login_info())["user_id"]
    head_msg = [MessageSegment.image(f"file:///{Path(WARNING_PATH +'fake_msg.png').absolute()}")]
    head = [await get_node(bot_qid, gid, head_msg)]

    for i in qid:
        head.append(await get_node(i, gid, content))

    return head


async def get_node(qid: int, gid: int, content: list):
    """
    构造合并转发消息节点
    参见 https://docs.go-cqhttp.org/cqcode/#%E5%90%88%E5%B9%B6%E8%BD%AC%E5%8F%91%E6%B6%88%E6%81%AF%E8%8A%82%E7%82%B9
    """
    node = {
        "type": "node",
        "data": {
            "name": "假的_" + (await get_group_member_info(gid, qid))["card"] + "_仅供娱乐",
            "uin": qid,
            "content": [{"type": i["type"], "data": i["data"]} for i in content]
        }
    }
    return node
