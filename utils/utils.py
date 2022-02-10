import datetime
import time

from httpx import AsyncClient


async def get_json(url: str, params=None):
    if params is None:
        params = {}
    async with AsyncClient() as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/54.0.2840.99 Safari/537.36"}
        res = await client.get(url, params=params, headers=headers, timeout=30)
    res.raise_for_status()
    return res.json()


# 与当前相差天数
def get_diff_days_2_now(date_str):
    now_time = time.localtime(time.time())
    compare_time = time.strptime(date_str, "%Y-%m-%d")
    # 比较日期
    date1 = datetime.datetime(
        compare_time[0], compare_time[1], compare_time[2])
    date2 = datetime.datetime(now_time[0], now_time[1], now_time[2])
    diff_days = (date2 - date1).days
    return diff_days
