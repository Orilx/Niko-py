import json
import requests
import time
import datetime

def get_json(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}
    res = requests.get(f"{url}", headers=headers)
    return json.loads(res.text)

# 与当前相差天数
def get_diff_days_2_now(date_str):
    now_time = time.localtime(time.time())
    compare_time = time.strptime(date_str, "%Y-%m-%d")
    # 比较日期
    date1 = datetime.datetime(compare_time[0], compare_time[1], compare_time[2])
    date2 = datetime.datetime(now_time[0], now_time[1], now_time[2])
    diff_days = (date2 - date1).days
    return diff_days