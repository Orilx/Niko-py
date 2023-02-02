import asyncio
import re
import time
from typing import List, Union

from loguru import logger
from lxml import etree
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import MessageSegment

from utils.config_util import add_sub_config
from utils.cq_utils import get_bot_info
from utils.msg_util import ForwardMsg
from utils.utils import get_json, get_page

driver = get_driver()
super_group = driver.config.super_group


class CovidInfoQindao:
    covid_info = add_sub_config(
        "青岛疫情信息",
        "covid_info",
        {
            "base_url": "http://wsjkw.qingdao.gov.cn/ztzl/xgfyyqfk/yqxx/",
            "old_num": 1365,
        },
    )

    tem_num = covid_info.get('old_num')
    base_url = covid_info.get("base_url")

    @classmethod
    async def get_new_releases(cls) -> List[int]:
        """
        获取最新发布公告的编号
        """
        # 记录新发布公告的编号
        new_releases = []
        old_num = cls.covid_info.get("old_num")
        # 回滚时使用
        cls.tem_num = old_num

        try:
            index_page = await get_page(cls.base_url)
            matcher = re.search(r'var RECORD_COUNT="([\s\S]+)";', index_page)
            assert matcher
            trsItemCount = int(matcher.group(1))
        except Exception as e:
            logger.warning("最新公告编号获取失败")
            trsItemCount = old_num

        for i in range(trsItemCount, old_num, -1):
            new_releases.append(i)

        cls.covid_info.set("old_num", trsItemCount)
        await cls.covid_info.save_file()

        return new_releases

    @classmethod
    async def get_text(cls, curNum: int) -> dict:
        """
        获取公告正文
        """
        # 构造获取正文对应 json 数据的链接
        curPath = str(curNum)[:2]

        json_url = (
            f"{cls.base_url}{curPath}/{curNum}.json?v={int(round(time.time() * 1000))}"
        )

        try:
            # 获取 json 中正文网页的链接
            page_url = (await get_json(json_url))["FILEURL"]
        except Exception as e:
            logger.warning("获取公告信息失败")
            return {
                "index": curNum,
                "title": "获取公告信息失败",
                "text": "",
                "url": json_url,
                "signature": "",
                "created_at": "",
            }

        try:
            # 获取正文网页内容
            text_page = await get_page(page_url)
        except Exception as e:
            logger.warning("获取公告正文失败")
            return {
                "index": curNum,
                "title": "获取公告正文失败",
                "text": "",
                "url": page_url,
                "signature": "",
                "created_at": "",
            }

        # 解析正文
        page = etree.HTML(text_page, parser=etree.HTMLParser(encoding="utf-8"))
        title = page.xpath("//title/text()")[0]
        text = page.xpath(
            "//div[@class='news-cont']//div[@class='view TRS_UEDITOR trs_paper_default trs_web']/p/text()"
        )

        # 处理文字
        text = [i.replace("\u2002", "") for i in text]
        main_text = text[:-2]
        signature = text[-2]
        created_at = text[-1]

        return {
            "index": curNum,
            "title": title,
            "text": main_text,
            "url": page_url,
            "signature": signature,
            "created_at": created_at,
        }

    @classmethod
    async def check_update(cls) -> Union[ForwardMsg, None]:
        """
        检查是否有新的公告
        """
        new_releases = await cls.get_new_releases()

        if not new_releases:
            return None

        # 构造转发消息链
        bot_qid = (await get_bot_info())["user_id"]
        head = ForwardMsg(bot_qid, "📣 疫情信息更新")

        for index in new_releases:
            data = await cls.get_text(index)
            logger.success(f'检查到青岛疫情信息更新：[{index}]')

            head.append_msg(bot_qid, f'{data["title"]} [{data["index"]}]\n============\n' +
                        f'📝：{data["signature"]}\n📅：{data["created_at"]}\n============\n{data["url"]}')

            if data["text"]:
                head.extend_msg(bot_qid, data["text"])
            else:
                head.append_msg(bot_qid, f'[{data["index"]}] {data["title"]}\n{data["url"]}')

            await asyncio.sleep(1)

        return head

    @classmethod
    async def roll_back(cls):
        """
        消息发送失败时回滚
        """
        cls.covid_info.set('old_num', cls.tem_num)
        await cls.covid_info.save_file()
