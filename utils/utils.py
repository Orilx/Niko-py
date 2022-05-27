import datetime
import time

from httpx import AsyncClient
import nonebot.adapters.onebot.v11.bot
from nonebot import logger
from nonebot.adapters.onebot.v11 import exception


async def send_group_msg(group_id: int, msg):
    """
    主动向群组发送消息
    """
    try:
        await nonebot.get_bot().call_api('send_group_msg', **{
            'message': msg,
            'group_id': group_id
        })
    except exception.NetworkError as ne:
        logger.warning(f'向{group_id}发送：{str(msg)[:20]}失败,{repr(ne)}')
        return False
    else:
        return True


async def send_group_forward_msg(group_id: int, msg):
    """
    发送合并转发 (群)
    """
    try:
        await nonebot.get_bot().call_api('send_group_forward_msg', **{
            'group_id': group_id,
            'messages': msg
        })
    except exception.NetworkError as ne:
        logger.warning(f'向{group_id}发送 合并转发 失败,{repr(ne)}')
        return False
    else:
        return True


async def get_group_member_info(group_id, user_id):
    """
    获取群成员信息
    """
    info = await nonebot.get_bot().call_api('get_group_member_info', **{
        'group_id': group_id,
        'user_id': user_id
    })
    return info


async def get_login_info():
    """
    获取登录号信息
    """
    info = await nonebot.get_bot().call_api('get_login_info')
    return info


async def get_json(url: str, params=None, headers=None):
    if params is None:
        params = {}
    async with AsyncClient() as client:
        if headers:
            client.headers = headers
        else:
            client.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/54.0.2840.99 Safari/537.36"}
        res = await client.get(url, params=params, timeout=30)
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
