from pathlib import Path

import requests
import datetime

from utils.config_util import Config
from utils.utils import get_diff_days_2_now


class scheduleConfig(Config):
    """
    配置文件管理类
    """

    def __init__(self):
        path = Path('data/c_schedules/cs_config.yaml')
        super().__init__(path, {
            "userInfo": {
                "account": "",
                "password": ""
            },
            "start_date": ""  # 开学日期
        })

    def get_user_info(self):
        return self.source_data["userInfo"]

    def get_start_date(self):
        return self.source_data["start_date"]


s = scheduleConfig()

weekday = datetime.datetime.now().weekday() + 1
week = get_diff_days_2_now(s.get_start_date()) // 7 + 1


class SW(object):
    def __init__(self, account, password):
        self.url = "http://jwgl.sdust.edu.cn/app.do"
        self.account = account
        self.password = password
        self.session = self.login()

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Mobile; Android 6.0.1;C107-9 Build/FRF91 )",
        "Referer": "https://www.baidu.com",
        "Accept-encoding": "gzip, deflate, br",
        "Accept-language": "zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2",
        "Cache-control": "max-age=0"
    }

    def login(self):
        params = {
            "method": "authUser",
            "xh": self.account,
            "pwd": self.password
        }
        session = requests.Session()
        req = session.get(self.url, params=params, timeout=5, headers=self.HEADERS)
        self.HEADERS["token"] = req.json()["token"]
        return session

    def get_handle(self, params):
        req = self.session.get(self.url, params=params, timeout=5, headers=self.HEADERS)
        return req

    def get_class_info(self, zc) -> list:
        params = {
            "method": "getKbcxAzc",
            "zc": zc,
            "xh": self.account
        }
        req = self.get_handle(params)
        return req.json()


class scheduleManager(Config):
    """
    TODO 待完善
         添加手动刷新方法
         实验或其他不排入课表的课程单独存入一个文件供查询，提供方法通过会话手动添加
    """

    def __init__(self):
        path = Path('data/c_schedules/cs_main_data.yaml')
        super().__init__(path, {0: {}, 1: {}})

    def update_data(self):
        Q = SW(**s.get_user_info())
        for i in range(2):
            data = Q.get_class_info(week + i)
            if data == [None]:
                break
            for d in data:
                # 过滤掉周六和周日的课程
                if d.get("kcsj")[0] not in [str(i) for i in range(6)]:
                    continue
                self.source_data[i][d.get("kcsj")] = {
                    "c_name": d.get("kcmc"),
                    "c_room": d.get("jsmc"),
                    "t_name": d.get("jsxm")
                }
        self.save_file(self.source_data)
        return self.source_data

    def get_cs_today(self):
        ans = {}
        for k, v in self.source_data[0].items():
            if k[0] == str(weekday):
                ans[k] = (self.source_data[0][k])
        return ans

    def wipe_data(self):
        self.__init__()


cs_manager = scheduleManager()
