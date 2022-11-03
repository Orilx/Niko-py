from nonebot.adapters.onebot.v11 import MessageSegment


class NodeMsg:
    def __init__(
            self, qid: int, msg: list[MessageSegment], nick_name: str = ""
    ) -> None:
        self.qid = qid
        self.msg = msg
        self.nick_name = nick_name


class NodeMsgList:
    def __init__(self, qid: int, msg: list[MessageSegment], nick_name: str = ""):
        self.node_list = [NodeMsg(qid, msg, nick_name)]

    def append(self, qid: int, msg: list[MessageSegment], nick_name: str = ""):
        self.node_list.append(NodeMsg(qid, msg, nick_name))

    def get(self):
        return self.node_list


def poke_cq(qid: int) -> MessageSegment:
    return MessageSegment("poke", {"qq": qid})
