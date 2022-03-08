from pathlib import Path
from enum import Enum
import requests
import datetime
from nonebot import logger

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
            "start_date": "",  # 开学日期
            "location": "黄岛",
            "enable": False  # 是否启用(开学
        })

    def get_user_info(self):
        return self.source_data["userInfo"]

    def get_start_date(self):
        return self.source_data["start_date"]

    def get_location(self):
        return self.source_data["location"]

    def is_begin(self):
        s_date = self.source_data["start_date"]
        return get_diff_days_2_now(s_date) >= 0


s_config = scheduleConfig()


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


class StatusCode(Enum):
    """状态码枚举类"""

    OK = (0, '操作成功')
    ERROR = (-1, '错误')
    SERVER_ERR = (101, '强智系统登录失败')
    SC_ERR = (102, '获取课表信息失败')
    CONFLICT_ERR = (201, '存在冲突课程，请检查')

    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def errmsg(self):
        """获取状态码信息"""
        return self.value[1]


class scheduleManager(Config):
    """
    课表管理类
    TODO 添加课表检索
    """

    def __init__(self):
        path = Path('data/c_schedules/cs_main_data.yaml')
        super().__init__(path, {'main_table': {}, 'sub_table': {}, "black_list": []})

    def refresh_data(self, p: bool = False):
        """
        更新课表
        参数p为True时获取下周课表
        """
        # 应该没啥用的异常处理
        try:
            Q = SW(**s_config.get_user_info())
        except Exception as e:
            logger.error(f"登录失败,{repr(e)}")
            return StatusCode.SERVER_ERR
        else:
            # 当前日期距离开学几周
            week = get_diff_days_2_now(s_config.get_start_date()) // 7 + 1
            try:
                if not p:
                    week += 1
                data = Q.get_class_info(week)
            except Exception as e:
                logger.error(f"获取课表信息失败,{repr(e)}")
                return StatusCode.SC_ERR
            # if data.get("state") != 1:
            #     return StatusCode.SERVER_ERR
            self.wipe_data()
            for d in data:
                # 过滤掉周六和周日的课程
                if d.get("kcsj")[0] not in [str(i) for i in range(6)]:
                    continue
                self.source_data['main_table'][d.get("kcsj")] = {
                    "c_name": d.get("kcmc"),
                    "c_room": d.get("jsmc"),
                    "t_name": d.get("jsxm")
                }
        self.save_file()
        return self.check_table()

    def update_data(self, c_name, c_time: int, c_room, c_start_week: int, c_end_week: int):
        """
        手动添加数据到 sub_table, 若表中已有返回 False
        课程名称，节次，教室，开始/结束周次
        TODO 可能存在一个时间对应多个在不同周的课的情况,目前不知道该怎么处理
        """
        if c_time in self.source_data['sub_table']:
            return StatusCode.CONFLICT_ERR

        self.source_data['sub_table'][c_time] = {
            "c_name": c_name,
            "c_room": c_room,
            "c_start_week": int(c_start_week),
            "c_end_week": int(c_end_week)
        }
        self.save_file()
        return self.refresh_data()

    def del_data(self, no: int):
        li = self.get_sub_table_list()
        key = li[no-1]
        self.source_data["sub_table"].pop(key)
        self.save_file()
        return StatusCode.OK

    def get_sub_table_name_list(self):
        """
        返回sub_table中课程的详细信息
        """
        li = self.get_sub_table_list()
        if not li:
            return '列表为空~'
        else:
            sub_table = self.source_data['sub_table']
            re_str = ''
            i = 1
            for item in li:
                re_str += f'{i}. {sub_table[item]["c_name"]}, {item}' \
                          f', {sub_table[item]["c_start_week"]}-{sub_table[item]["c_end_week"]}周\n'
                i += 1
            return re_str

    def get_sub_table_list(self) -> list:
        sub_table = self.source_data['sub_table']
        re_list = [i for i in sub_table]
        return re_list

    def check_table(self):
        """
        检查两个表中是否含有冲突项目
        并去除 sub_table 中已结束的课程
        """
        # 当前日期距离开学几周
        week = get_diff_days_2_now(s_config.get_start_date()) // 7 + 1
        # 计算今天是周几
        weekday = datetime.datetime.now().weekday() + 1

        if weekday in [5, 6]:
            week += 1
        main_table = self.source_data['main_table']
        sub_table = self.source_data['sub_table']
        black_list = self.get_black_list()
        s_code = StatusCode.OK

        bak_main_table = {}
        bak_sub_table = {}
        # 删除在黑名单里的课程
        for k, v in main_table.items():
            if v.get("c_name") not in black_list:
                bak_main_table[k] = v
        self.source_data['main_table'] = bak_main_table

        for k, v in sub_table.items():
            # 删除已经结束的课程
            # 删除在黑名单里的课程
            if week in range(v["c_end_week"] + 1) and v.get("c_name") not in black_list:
                bak_sub_table[k] = v
                continue
            # 是否有冲突的课程
            if k in main_table and week in range(v["c_start_week"], v["c_end_week"] + 1):
                s_code = StatusCode.CONFLICT_ERR
        self.source_data['sub_table'] = bak_sub_table
        self.save_file()
        return s_code

    def add_black_list(self, name: str):
        self.source_data["black_list"].append(name)
        return self.check_table()

    def rm_black_list(self, name: str):
        self.source_data["black_list"].pop(name)
        return self.check_table()

    def get_black_list(self):
        return self.source_data["black_list"]

    def get_cd_list(self):
        """
        获取当前数据文件中所有的课程名
        """
        resp = []
        main_table = self.source_data['main_table']
        sub_table = self.source_data['sub_table']
        for k, v in main_table.items():
            resp.append(v.get("c_name"))
        for k, v in sub_table.items():
            resp.append(v.get("c_name"))
        return list(set(resp))

    def get_cs_today(self):
        """
        获取今天的课表
        """
        time_table = {'0102': '一', '0304': '二', '0506': '三', '0708': '四', '0910': '五'}
        msg = '今日课表：'

        if not s_config.is_begin():
            return '别急，还没开学呢~'

        # 计算今天是周几
        weekday = datetime.datetime.now().weekday() + 1
        week = get_diff_days_2_now(s_config.get_start_date()) // 7 + 1
        cs_li = {}
        for k, v in self.source_data["main_table"].items():
            if k[0] == str(weekday):
                cs_li[k] = v
        for k, v in self.source_data["sub_table"].items():
            if k[0] == str(weekday) and week in range(v['c_start_week'],v["c_end_week"]+1):
                cs_li[k] = v

        for k in sorted(cs_li):
            msg += f'\n第{time_table.get(k[1:5])}节  {cs_li[k]["c_name"]}, {cs_li[k]["c_room"]}'
        return msg

    def get_cs_week(self):
        """
        获取本周的课表
        """
        week = get_diff_days_2_now(s_config.get_start_date()) // 7 + 1
        week_table = {'1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六', '7': '日'}
        time_table = {'0102': '一', '0304': '二', '0506': '三', '0708': '四', '0910': '五'}
        msg = '本周课表：'

        if not s_config.is_begin():
            return '别急，还没开学呢~'

        cs_li = {}
        for k, v in self.source_data["main_table"].items():
            cs_li[k] = v
        for k, v in self.source_data["sub_table"].items():
            if week in range(v['c_start_week'],v["c_end_week"]+1):
                cs_li[k] = v

        for i in sorted(cs_li):
            msg += f'\n周{week_table.get(i[0])} 第{time_table.get(i[1:5])}节  {cs_li[i]["c_name"]}, {cs_li[i]["c_room"]}'
        return msg

    def wipe_data(self):
        self.source_data["main_table"] = {}
        self.save_file()


cs_manager = scheduleManager()
