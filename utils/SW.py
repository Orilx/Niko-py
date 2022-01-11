# Fork from: https://github.com/WindrunnerMax/SHST

import time
import requests
import re
import os
import json
import datetime


class SW(object):
    def __init__(self, account, password,url):
        super(SW, self).__init__()
        self.url = url
        self.account = account
        self.password = password
        self.session = self.login()
    
    HEADERS = {
        "User-Agent":"Mozilla/5.0 (Linux; U; Mobile; Android 6.0.1;C107-9 Build/FRF91 )",
        "Referer": "http://www.baidu.com",
        "Accept-encoding": "gzip, deflate, br",
        "Accept-language": "zh-CN,zh-TW;q=0.8,zh;q=0.6,en;q=0.4,ja;q=0.2",
        "Cache-control": "max-age=0"
    }

    def login(self):
        params = {
            "method" : "authUser",
            "xh" : self.account,
            "pwd" : self.password
        }
        session = requests.Session()
        req = session.get(self.url, params = params, timeout = 5, headers = self.HEADERS)
        s = json.loads(req.text)
        # print(s)
        if s["flag"] != "1" : exit(0)
        self.HEADERS["token"] = s["token"]
        return session

    

    def get_handle(self,params):
        req = self.session.get(self.url, params = params ,timeout = 5 ,headers = self.HEADERS)
        return req

    def get_student_info(self):
        params = {
            "method" : "getUserInfo",
            "xh" : self.account
        }
        req = self.get_handle(params)
        print(req.text)
    
    def get_current_time(self):
        params = {
            "method" : "getCurrentTime",
            "currDate" : datetime.datetime.now().strftime("%Y-%m-%d")
        }
        req = self.get_handle(params)
        print(req.text)
        return req.text

    def get_class_info(self,zc = -1):
        s = json.loads(self.get_current_time())
        params={
            "method" : "getKbcxAzc",
            "xnxqid" : s["xnxqh"],
            "zc" : s["zc"] if zc == -1 else zc,
            "xh" : self.account
        }
        req = self.get_handle(params)
        return req.text

    def get_classroom_info(self,idleTime = "allday"):
        params={
            "method" : "getKxJscx",
            "time" : datetime.datetime.now().strftime("%Y-%m-%d"),
            "idleTime" : idleTime
        }
        req = self.get_handle(params)
        print(req.text)

    def get_grade_info(self,sy = ""):
        params={
            "method" : "getCjcx",
            "xh" : self.account,
            "xnxqid" : sy
        }
        req = self.get_handle(params)
        print("全部成绩" if sy == "" else sy)
        s = json.loads(req.text)
        if s[0] != None :
            s = json.loads(req.text)
            for x in s:
                print("%s   %d   %s" % (str(x["zcj"]),x["xf"],x["kcmc"]))
            print("绩点：" + str(self.get_gp(s)))
        else :
            print("空")

    def get_exam_info(self):
        params={
            "method" : "getKscx",
            "xh" : self.account,
        }
        req = self.get_handle(params)
        print(req.text)

    def get_gp(self,data):
        GP = 0.0
        credit = 0.0
        for x in data:
            credit += x["xf"]
            if  x["zcj"] == "优":
                GP += (4.5 * x["xf"])
            elif x["zcj"] == "良":
                GP += (3.5 * x["xf"])
            elif x["zcj"] == "中":
                GP += (2.5 * x["xf"])
            elif x["zcj"] == "及格":
                GP += (1.5 * x["xf"])
            elif x["zcj"] == "不及格":
                GP += 0 
            else :
                if float(x["zcj"]) >= 60:
                   GP += (((float(x["zcj"])-60)/10+1) * x["xf"])
        return GP/credit

    def get_class(self, account: str, password: str) -> list:
        url = "http://jwgl.sdust.edu.cn/app.do"
        Q = SW(account, password, url)
        ls = []
        i = 1
        while True:
            js = json.loads(Q.get_class_info(i))
            if js == [None]:
                # print("finished.")
                break
            i += 1
            for item in js:
                course = item['kcmc']
                room = item['jsmc']
                info = item['kcsj']
                teacher = item['jsxm']
                week = item['kkzc'].split('-')
                start_week = week[0]
                if len(week) == 1:
                    end_week = start_week
                else:
                    end_week = week[1]
                ls.append(f"{info}_{course}_{room}_{teacher}_{start_week}_{end_week}")
        # 去重，排序
        res = list(set(ls))
        res.sort()
        return res
