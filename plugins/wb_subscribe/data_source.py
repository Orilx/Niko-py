import asyncio
import json
import re
import time
from pathlib import Path
from typing import List, Tuple, Union

from lxml import etree
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (GroupMessageEvent, Message,
                                         MessageSegment)
from nonebot.log import logger

from utils.config_util import FileManager
from utils.cq_utils import get_bot_info, send_group_forward_msg, send_group_msg
from utils.msg_util import ForwardMsg
from utils.utils import get_json, get_page, get_data

super_group = get_driver().config.super_group


def format_time(time_str):
    return time.strftime(
        "%Y-%m-%d %H:%M:%S", time.strptime(time_str, "%a %b %d %H:%M:%S %z %Y")
    )


async def get_img(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26",
        "Referer": "https://m.weibo.cn/"
    }
    img = await get_data(url, headers=headers)
    return img.content


async def get_user_info(uid):
    """
    获取微博账号信息
    """
    params = {"type": "uid", "value": uid}
    info = await get_json(
        "https://m.weibo.cn/api/container/getIndex", params=params
    )
    return info["data"]["userInfo"]["screen_name"]


async def get_latest_items(uid: int, num: int = 3) -> List[dict]:
    """
    获取最近更新的微博，可指定条数，默认最多三条
    num 为 0 时获取最新一条
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
        return []
    else:
        card_list = {}
        for card in first_page["data"]["cards"]:
            if card["card_type"] == 9:
                # 过滤转发微博
                if "retweeted_status" in card["mblog"]:
                    continue
                mid = card["mblog"]["mid"]
                card_list[mid] = card["mblog"]

        # 获取最新微博
        if not num:
            x = max([i for i in card_list], default=0)
            # 返回最新微博 raw_post
            return [card_list[x]]

        sorted_keys = sorted(card_list.keys(), reverse=True)
        current_mid = WbSubConfig.get_last_mid(uid)
        post_list = []
        cnt = 0
        for i in sorted_keys:
            if int(i) <= current_mid or cnt > num - 1:
                break

            post_list.append(card_list[i])
            cnt += 1

        # 返回微博 raw_post 列表和最新一条对应的 mid
        return post_list


async def get_latest_item(uid: int) -> dict:
    """
    获取最新一条微博
    """
    return (await get_latest_items(uid, 0))[0]


def _get_text(raw_text: str) -> str:
    text = raw_text.replace("<br />", "\n")
    return etree.HTML(text, etree.HTMLParser(encoding="utf-8")).xpath('string(.)')


async def parse(raw_post: dict) -> dict:
    mid = raw_post["mid"]

    # 含有 '展开全文' 的微博
    if raw_post.get("isLongText"):
        try:
            res = await get_page(f"https://m.weibo.cn/detail/{mid}")
            match = re.search(r'"status": ([\s\S]+),\s+"call"', res)
            # assert match, res
            assert match
            raw_post = json.loads(match.group(1))
        except Exception as e:
            logger.warning(f"获取长微博数据失败, mid: {mid}, {repr(e)}")

    info = raw_post.get("page_info", {})

    pics = []
    if info and info["type"] == "video":
        pics.append(await get_img(info["page_pic"]["url"]))
    elif raw_post.get("pics"):
        for i in raw_post.get("pics"):
            pics.append(await get_img(i["large"]["url"]))

    data = {
        "mid": raw_post["mid"],
        "text": _get_text(raw_post["text"]),
        "url": f'm.weibo.cn/detail/{raw_post["bid"]}',
        "screen_name": raw_post["user"]["screen_name"],
        # "pic_urls": pic_urls,
        "pics": pics,
        "created_at": format_time(raw_post["created_at"]),
    }

    return data


async def format_mblog(raw_post) -> Union[dict, Message, str]:
    """
    将消息格式化
    """
    post_data = await parse(raw_post)

    if not post_data.get("mid"):
        return "该账号暂无最新微博~"

    msg = f'{post_data["screen_name"]}\n============\n{post_data["text"]}\n'

    # pic_urls: list[str] = post_data["pic_urls"]
    pics = post_data["pics"]

    # 图片多于三张时，交给 send_mblog_msg 构造转发消息
    if len(pics) > 4:
        return post_data
    else:
        for i in pics:
            msg += MessageSegment.image(i) + "\n"

    msg += f'============\n⏰: {post_data["created_at"]}\n🔗: {post_data["url"]}'

    return msg


async def send_mblog(gid: int, post_data: dict) -> bool:
    mblog = await format_mblog(post_data)
    if isinstance(mblog, Message) or isinstance(mblog, str):
        return await send_group_msg(gid, mblog)
    else:
        # pic_urls: list[str] = mblog["pic_urls"]
        pics = mblog["pics"]

        bot_qid = (await get_bot_info())["user_id"]

        f'⏰: {mblog["created_at"]}\n🔗: {mblog["url"]}'

        # 构造转发消息链
        head = ForwardMsg(bot_qid, mblog["text"], mblog["screen_name"])

        # for i in pic_urls:
        #     print(i)
        #     head.append(bot_qid, Message(MessageSegment.image(i)), mblog["screen_name"])

        for i in pics:
            head.append_msg(bot_qid, Message(MessageSegment.image(i)), mblog["screen_name"])
        head.append_msg(bot_qid, f'⏰: {mblog["created_at"]}\n🔗: {mblog["url"]}', mblog["screen_name"])

        return await send_group_forward_msg(gid, head)


async def check_update():
    # logger.info('开始检查微博更新...')
    for uid in WbSubConfig.get_check_list():
        # logger.info(f'检查 {v.get("screen_name")} 微博更新...')
        mblog_list = await get_latest_items(uid)
        screen_name = WbSubConfig.get_screen_name(uid)

        if not mblog_list:
            continue

        latest_mid = int(max([i["mid"] for i in mblog_list]))
        if latest_mid == 0:
            # logger.warning(f'获取微博失败!')
            continue
        else:
            logger.info(f'检查到 {screen_name} 微博更新...')

        msg_list = []
        for mblog in mblog_list:
            msg_list.append(mblog)

        # 遍历列表发送消息
        for g_id in WbSubConfig.get_sub_list(uid):
            cnt = 0
            log_info = f'向 {g_id} 发送：{screen_name}'

            # 倒序遍历
            for item in msg_list[::-1]:

                if await send_mblog(g_id, item):
                    logger.success(f'{log_info} [{cnt}]')
                else:
                    logger.warning(f'{log_info} [{cnt}] 失败')

                await asyncio.sleep(3)
                cnt += 1
            logger.success(f"向 {g_id} 发送完成")

        # 更新最新 mid
        WbSubConfig.modify_mid(uid, latest_mid)


class WbSubConfig:
    """
    订阅文件存储位置
    """
    path = Path("data/wb_sub_list.yaml")
    data_manager = FileManager(path, {
        "6104718631": {
            "screen_name": "YearProgress",
            "last": 0,
            "group_ids": [int(i) for i in super_group],
        }
    })

    @classmethod
    def save(cls):
        cls.data_manager.save_file()

    @classmethod
    def modify_mid(cls, uid: str, mid: int):
        """
        修改最新微博对应的 mid
        """
        cls.data_manager.source_data[uid]["last"] = mid
        cls.save()

    @classmethod
    async def add_container(cls, uid: int, group_id: int, mid: int):
        screen_name = await get_user_info(uid)
        cls.data_manager.source_data[uid] = {
            "screen_name": screen_name,
            "last": mid,
            "group_ids": [group_id],
        }
        cls.save()

    @classmethod
    async def add_subscribe(cls, uid: int, group_id: int, mid: int):
        """
        添加订阅
        TODO 待重构
        """
        if not cls.data_manager.source_data.get(uid):
            await cls.add_container(uid, group_id, mid)
            return cls.data_manager.source_data[uid]["screen_name"]

        id_list = cls.data_manager.source_data[uid]["group_ids"]
        if group_id in id_list:
            return
        cls.data_manager.source_data[uid]["group_ids"].append_msg(group_id)
        cls.save()
        return cls.data_manager.source_data[uid]["screen_name"]

    @classmethod
    async def rm_subscribe(cls, uid: str, group_id: int):
        """
        移除订阅
        """
        cls.data_manager.source_data[uid]["group_ids"].remove(group_id)
        cls.save()

    @classmethod
    def get_container_list(cls, group_id: int) -> dict:
        """
        获取微博账号的container_id
        根据文件中顺序生成container_list
        """
        container_list = {}
        num = 0
        for k, v in cls.data_manager.source_data.items():
            if group_id in v["group_ids"]:
                container_list[str(num)] = k
                num += 1
        return container_list

    @classmethod
    def group_sub_list(cls, group_id: int) -> dict:
        """
        获取该群组订阅微博名称列表
        """
        sub_list = {}
        num = 0
        for k, v in cls.data_manager.source_data.items():
            if group_id in v["group_ids"]:
                sub_list[str(num)] = v.get("screen_name")
                num += 1
        return sub_list

    @classmethod
    def get_check_list(cls) -> list:
        """
        获取要检查更新的所有微博用户对应的uid
        """
        check_list = []
        for k, v in cls.data_manager.source_data.items():
            # 跳过订阅群组为空的微博记录
            if not v.get("group_ids"):
                # logger.warning(f'{v.get("screen_name")} skip here!!!!!')
                continue
            check_list.append(k)

        return check_list

    @classmethod
    def get_sub_list(cls, uid: str) -> list:
        """
        获取订阅该微博的所有群组
        """
        return cls.data_manager.source_data[uid]["group_ids"]

    @classmethod
    def get_last_mid(cls, uid: int) -> int:
        """
        获取机器人最后发送的 uid 对应用户的微博编号
        """
        return cls.data_manager.source_data[uid]["last"]

    @classmethod
    def get_screen_name(cls, uid: int) -> str:
        """
        获取微博 uid 对应的用户名
        """
        return cls.data_manager.source_data[uid]["screen_name"]
