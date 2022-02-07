import time
from pathlib import Path

from bs4 import BeautifulSoup
from nonebot import get_driver
from utils.config_util import Config
from utils.utils import get_json

super_group = get_driver().config.super_group


def format_time(time_str):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time_str, "%a %b %d %H:%M:%S %z %Y"))


async def get_info(uid):
    """
    获取微博账号信息
    """
    params = {
        "type": "uid",
        "value": uid
    }
    info = await get_json('https://m.weibo.cn/api/container/getIndex', params=params)
    return info["data"]["userInfo"]["screen_name"]


async def get_data(uid):
    """
    获取最新一条微博
    """
    params = {
        "type": "uid",
        "value": uid,
        "containerid": "107603" + uid,
        "page": 1,
    }
    first_page = await get_json('https://m.weibo.cn/api/container/getIndex', params=params)

    data = {}
    for card in first_page["data"]["cards"]:
        if card["card_type"] == 9:
            # 过滤转发微博
            if "retweeted_status" in card["mblog"]:
                continue
            bid = card["mblog"]["bid"]
            soup = BeautifulSoup(card["mblog"]["text"], "lxml")
            id_ = card["mblog"]["id"]
            created_at = card["mblog"]["created_at"]
            info = card["mblog"].get("page_info", {})
            # print(str(info))
            if info and info["type"] == "video":
                images = [info["page_pic"]["url"]]
            else:
                images = [i["large"]["url"] for i in card["mblog"].get("pics", [])]
            data[id_] = {
                "bid": id_,
                "text": soup.get_text("\n", strip=True),
                "url": "m.weibo.cn/status/" + bid,
                "screen_name": card["mblog"]["user"]["screen_name"],
                "info": info,
                "images": images,
                "created_at": format_time(created_at)
            }
    # 找到最新一条微博（？
    x = max([i for i in data])
    return data[x]


class WbSubConfig(Config):

    def __init__(self):
        """
        订阅文件存储位置
        """
        path = Path('data/wb_sub_list.yaml')
        super().__init__(path, {
            "6104718631": {
                "screen_name": "YearProgress",
                "last": 0,
                "group_ids": [int(i) for i in super_group]
            }
        })

    # def get_groups(self, uid: str) -> list:
    #     return self.source_data.get(uid)

    def save(self):
        super().save_file(self.source_data)

    def modify_bid(self, container: str, bid: int):
        """
        修改最新微博对应的bid
        """
        self.source_data[container]["last"] = bid
        self.save()

    async def add_container(self, uid: str, group: int):
        screen_name = await get_info(uid)
        self.source_data[uid] = {
            "screen_name": screen_name,
            "last": 0,
            "group_ids": [group]
        }
        self.save()

    async def add_subscribe(self, uid: str, group_id: int):
        """
        添加订阅
        TODO 待重构
        """
        if not self.source_data.get(uid):
            await self.add_container(uid, group_id)
            return self.source_data[uid]["screen_name"]

        id_list = self.source_data.get(uid)["group_ids"]
        if group_id in id_list:
            return None
        self.source_data[uid]["group_ids"].append(group_id)
        self.save()
        return self.source_data[uid]["screen_name"]

    async def rm_subscribe(self, uid: str, group_id: int):
        """
        移除订阅
        TODO
        """
        pass

    def group_sub_list(self, group_id: int) -> list:
        """
        获取该群组订阅微博列表
        """
        sub_list = []
        for k, v in self.source_data.items():
            if group_id in v["group_ids"]:
                sub_list.append(v.get("screen_name"))
        return sub_list

    def get_sub_list(self, uid: str) -> list:
        """
        获取订阅该微博的所有群组
        """
        return self.source_data.get(uid).get("group_ids")


wb_sub_config = WbSubConfig()
