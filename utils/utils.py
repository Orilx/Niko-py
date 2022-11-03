import datetime
import time
from httpx import AsyncClient, ConnectError


async def get_data(url: str, params=None, headers=None):
    if params is None:
        params = {}

    async with AsyncClient() as client:
        if headers:
            client.headers = headers
        else:
            client.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26"}
        res = await client.get(url, params=params, timeout=30)

    return res


async def get_page(url: str, params=None, headers=None) -> str:
    res = await get_data(url, params, headers)
    return res.text


async def get_json(url: str, params=None, headers=None):
    res = await get_data(url, params, headers)
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


def is_overlap(range_a: tuple, range_b: tuple):
    """
    检查两区间是否重叠
    传入参数为两个包含开始和结束周的元组
    """
    return max(range_a[0], range_b[0]) <= min(range_a[1], range_b[1])
