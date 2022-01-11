import sys
import time

from bs4 import BeautifulSoup
from httpx import AsyncClient, Response


def format_time(time_str):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(time_str, "%a %b %d %H:%M:%S %z %Y"))


async def get_info(uid, idx):
    async with AsyncClient() as client:
        info = await client.get("https://m.weibo.cn/api/container/getIndex", params={
            "type": "uid",
            "value": uid,
            "containerid": "107603" + uid,
            "page": idx,
        })
    info.raise_for_status()
    return info.json()["data"]


async def get_data(uid):
    first_page = await get_info(uid, 1)
    data = {}
    for card in first_page["cards"]:
        if card["card_type"] == 9:
            soup = BeautifulSoup(card["mblog"]["text"], "lxml")
            id_ = card["mblog"]["id"]
            created_at = card["mblog"]["created_at"]
            data[id_] = {
                "text": soup.get_text("\n", strip=True),
                "url": card["scheme"],
                "screen_name": card["mblog"]["user"]["screen_name"],
                "images": card["mblog"].get("pics", []),
                "created_at": format_time(created_at)
            }
    x = max([i for i in data])
    return data[x]
