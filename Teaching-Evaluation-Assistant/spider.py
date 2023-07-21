# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# spider.py 2019/1/18 10:18
import json
import config
import requests
from requests.exceptions import RequestException

from uniform_login import uniform_login_spider


def login(username, password):
    """登录，返回一个response"""
    try:
        JSESSIONID = uniform_login_spider.login(username, password, 'http://bkjws.sdu.edu.cn/f/j_spring_security_thauth_roaming_entry')
        config.HEADERS["Cookie"] = f"JSESSIONID={JSESSIONID}"
        return '"success"'
    except Exception as e:
        print(e)
        return None


def get_profile():
    """获得使用者姓名"""
    try:
        response = requests.post('http://bkjws.sdu.edu.cn/b/grxx/xs/xjxx/detail', headers=config.HEADERS)
        if response.status_code != 200 or '"success"' not in response.text:
            return None
        profile_json = json.loads(response.text)["object"]
        return {
            "姓名": profile_json["xm"],
            "学院": profile_json['xsm'],
            "专业名": profile_json['zym'],
            "班名": profile_json["bm"],
            "入学日期": profile_json['rxrq']
        }
    except RequestException:
        return None


def get_evaluation_list():
    """获得教评列表，前提：已登录"""
    try:
        response = requests.post('http://bkjws.sdu.edu.cn/b/pg/xs/list', data=config.EVALUATION_LIST_DATA, headers=config.HEADERS)
        if response.status_code == 200:
            return [
                {
                    'xnxq': i['xnxq'],
                    'kch': i['kch'],
                    'kcm': i['kcm'],
                    'jsm': i['jsm'],
                    'jsh': i['jsh'],
                    'pgcs': i['pgcs'],  # 评价次数
                }
                for i in json.loads(response.text)['object']['aaData']
            ]
    except Exception:
        return None

# def get_evaluation_html(xnxq, kch, jsh):
#     """获得教评页面，前提：已登录"""
#     data = {
#         'xnxq': xnxq,
#         'kch': kch,
#         'jsh': jsh,
#     }
#     try:
#         response = requests.post('http://bkjws.sdu.edu.cn/f/pg/xs/jrwq', headers=config.HEADERS, data=data)
#         soup = BeautifulSoup(response.text, 'lxml')
#         data2 = []
#         for i in soup.find_all('input', type='hidden'):
#             data2.append((i.get('name'), i.get('value')))
#         soup.find()
#         return soup
#     except RequestException:
#         return None

def default_evaluate_one_course(xnxq, kch, jsh):
    try:
        data = f'xnxq={xnxq}&kch={kch}&jsh={jsh}&{config.DEFALUT_EVALUATION_PARM}'
        response = requests.post('http://bkjws.sdu.edu.cn/b/pg/xs/add', data=data, headers=config.HEADERS)
        return 'success' in response.text if response.status_code == 200 else False
    except RequestException:
        return False

