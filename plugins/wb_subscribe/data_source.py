import json
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup as bs
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.log import logger
from utils.config_util import FileManager
from utils.cq_utils import get_group_member_info, get_login_info, send_group_msg, send_group_forward_msg
from utils.msg_util import NodeMsgList
from utils.utils import get_json, get_page

super_group = get_driver().config.super_group


def format_time(time_str):
    return time.strftime(
        "%Y-%m-%d %H:%M:%S", time.strptime(time_str, "%a %b %d %H:%M:%S %z %Y")
    )


async def get_user_info(uid):
    """
    获取微博账号信息
    """
    params = {"type": "uid", "value": uid}
    info = await get_json(
        "https://m.weibo.cn/api/container/getIndex", params=params
    )
    return info["data"]["userInfo"]["screen_name"]


async def get_latest_item(uid) -> dict:
    """
    获取最新一条微博
    """
    first_page = {}
    params = {
        "type": "uid",
        "value": uid,
        "containerid": f"107603{uid}",
        "page": 1,
    }
    try:
        first_page = await get_json(
            "https://m.weibo.cn/api/container/getIndex", params=params
        )
    except Exception as e:
        logger.warning(f"获取 {uid} 微博列表失败,{repr(e)}")
        return {}
    else:
        card_list = {}
        for card in first_page["data"]["cards"]:
            if card["card_type"] == 9:
                # 过滤转发微博
                if "retweeted_status" in card["mblog"]:
                    continue
                mid = card["mblog"]["mid"]
                card_list[mid] = card["mblog"]

        # 未获取到数据
        if not card_list:
            return {}

        x = max([i for i in card_list], default=0)

        # 返回最新微博对应 raw_post 数据
        return card_list[x]


def get_text(raw_text: str) -> str:
    # print(raw_text)
    text = raw_text.replace("<br />", "\n")
    return bs(text, "html.parser").text


async def parse(raw_post) -> dict:
    mid = raw_post["mid"]

    # 含有 '展开全文' 的微博
    if raw_post["isLongText"]:
        try:
            res = await get_page(f"https://m.weibo.cn/detail/{mid}")
            match = re.search(r'"status": ([\s\S]+),\s+"call"', res)
            # assert match, res
            assert match
            raw_post = json.loads(match.group(1))
        except Exception as e:
            logger.warning(f"获取长微博数据失败, mid: {mid}, {repr(e)}")

    info = raw_post.get("page_info", {})

    pic_urls = []
    if info and info["type"] == "video":
        pic_urls = [info["page_pic"]["url"]]
    elif raw_post.get("pics"):
        pic_urls = [i["large"]["url"] for i in raw_post.get("pics", [])]

    data = {
        "mid": raw_post["mid"],
        "text": get_text(raw_post["text"]),
        "url": "m.weibo.cn/status/" + raw_post["bid"],
        "screen_name": raw_post["user"]["screen_name"],
        "pic_urls": pic_urls,
        "created_at": format_time(raw_post["created_at"]),
    }

    return data


async def format_mblog(post_data) -> MessageSegment | Message | str:
    """
    将消息格式化
    """
    if not post_data.get("mid"):
        return "该账号暂无最新微博~"

    msg = MessageSegment.text(
        f'{post_data["screen_name"]}\n============\n{post_data["text"]}\n'
    )

    pic_urls: list[str] = post_data.get("pic_urls")
    # 没有图片时
    if not pic_urls:
        pass
    # 图片少于等于四张时，把所有图片放在单条消息里
    elif len(pic_urls) <= 4:
        for i in pic_urls:
            msg += MessageSegment.image(i) + "\n"
    # 图片多于三张时，交给 send_mblog_msg 构造转发消息
    else:
        return ""

    msg += f'============\n⏰: {post_data["created_at"]}\n🔗: {post_data["url"]}'
    return msg


async def send_mblog_msg(gid: int, post_data: dict) -> bool:
    msg = await format_mblog(post_data)

    if msg:
        return await send_group_msg(gid, msg)

    else:
        pic_urls: list[str] = post_data["pic_urls"]
        bot_qid = (await get_login_info())["user_id"]

        f'⏰: {post_data["created_at"]}\n🔗: {post_data["url"]}'

        # 构造转发消息链
        head = NodeMsgList(
            bot_qid, [MessageSegment.text(post_data["text"])], post_data["screen_name"]
        )

        for i in pic_urls:
            head.append(bot_qid, [MessageSegment.image(i)], post_data["screen_name"])

        head.append(
            bot_qid, [MessageSegment.text(f'⏰: {post_data["created_at"]}\n' +
                                          f'🔗: {post_data["url"]}')], post_data["screen_name"])

        return await send_group_forward_msg(gid, head)


async def get_data(uid) -> dict:
    raw_post = await get_latest_item(uid)
    if not raw_post:
        return {}
    return await parse(raw_post)


class WbSubConfig(FileManager):
    def __init__(self):
        """
        订阅文件存储位置
        """
        path = Path("data/wb_sub_list.yaml")
        super().__init__(
            path,
            {
                "6104718631": {
                    "screen_name": "YearProgress",
                    "last": 0,
                    "group_ids": [int(i) for i in super_group],
                }
            },
        )

    def save(self):
        super().save_file()

    def modify_mid(self, container: str, mid: int):
        """
        修改最新微博对应的 mid
        """
        self.source_data[container]["last"] = mid
        self.save()

    async def add_container(self, uid: str, group_id: int, mid: int):
        screen_name = await get_user_info(uid)
        self.source_data[uid] = {
            "screen_name": screen_name,
            "last": mid,
            "group_ids": [group_id],
        }
        self.save()

    async def add_subscribe(self, uid: str, group_id: int, mid: int):
        """
        添加订阅
        TODO 待重构
        """
        if not self.source_data.get(uid):
            await self.add_container(uid, group_id, mid)
            return self.source_data[uid]["screen_name"]

        id_list = self.source_data.get(uid)["group_ids"]
        if group_id in id_list:
            return
        self.source_data[uid]["group_ids"].append(group_id)
        self.save()
        return self.source_data[uid]["screen_name"]

    async def rm_subscribe(self, uid: str, group_id: int):
        """
        移除订阅
        """
        self.source_data[uid]["group_ids"].remove(group_id)
        self.save()

    def get_container_list(self, group_id: int) -> dict:
        """
        获取微博账号的container_id
        根据文件中顺序生成container_list
        """
        container_list = {}
        num = 0
        for k, v in self.source_data.items():
            if group_id in v["group_ids"]:
                container_list[str(num)] = k
                num += 1
        return container_list

    def group_sub_list(self, group_id: int) -> dict:
        """
        获取该群组订阅微博名称列表
        """
        sub_list = {}
        num = 0
        for k, v in self.source_data.items():
            if group_id in v["group_ids"]:
                sub_list[str(num)] = v.get("screen_name")
                num += 1
        return sub_list

    def get_sub_list(self, uid: str) -> list:
        """
        获取订阅该微博的所有群组
        """
        return self.source_data.get(uid).get("group_ids")


wb_sub_config = WbSubConfig()
