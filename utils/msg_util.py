from nonebot.adapters.onebot.v11 import MessageSegment, Message
from typing import Union, List


class NodeMsg:
    def __init__(self, qid: int, msg: Union[str, Message], nick_name: str = ""):
        self.qid = qid
        self.msg = msg
        self.nick_name = nick_name


class ForwardMsg(List[NodeMsg]):
    def __init__(self, qid: int, msg: Union[str, Message, list[str]], nick_name: str = ""):
        super().__init__()
        if isinstance(msg, Message) or isinstance(msg, str):
            self.append_msg(qid, msg, nick_name)
        else:
            self.extend_msg(qid, msg, nick_name)

    def append_msg(self, qid: int, msg: Union[str, Message], nick_name: str = ""):
        super().append(NodeMsg(qid, msg, nick_name))
        return self

    def extend_msg(self, qid: int, msg: List[str], nick_name: str = ""):
        for i in msg:
            self.append_msg(qid, i, nick_name)
        return self


def poke_cq(id: int) -> MessageSegment:
    return MessageSegment("poke", {"qq": id})
