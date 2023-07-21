# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Copyright 2018 ZhangT. All Rights Reserved.
# Author: ZhangT
# Author-Github: github.com/zhangt2333
# GPA-Spider.py 2018/2/10 20:31

import json
from config import generateMD5
import config
import requests
from requests.exceptions import RequestException


def set_Cookie():
    """统一程序中发送requests请求的所有cookie，即加到headers里面"""
    try:
        response = requests.get('http://bkjwxk.sdu.edu.cn/f/common/main')
        if response.status_code != 200:
            return False
        config.JSESSIONID = response.request._cookies._cookies
        config.JSESSIONID = str(config.JSESSIONID['bkjwxk.sdu.edu.cn']['/']['JSESSIONID'])[19:40]
        config.HEADERS["Cookie"] = f"JSESSIONID={config.JSESSIONID}"
        return True
    except RequestException:
        return False


def login(username, password):
    """登录，返回一个response"""
    data = f"j_username={username}&j_password={generateMD5(password)}"
    try:
        response = requests.post('http://bkjws.sdu.edu.cn/b/ajaxLogin', data=data, headers=config.HEADERS)
        return response.text if response.status_code == 200 else None
    except RequestException:
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


def get_now_score():
    """返回一个本学期成绩json"""
    try:
        response = requests.post('http://bkjws.sdu.edu.cn/b/cj/cjcx/xs/list', data=config.aoData,
                                 headers=config.HEADERS)
        if response.status_code == 200 and 'success' in response.text:
            return json.loads(response.text)
        return None
    except RequestException:
        return None


def get_past_score():
    """返回一个所谓历年成绩json"""
    try:
        response = requests.post('http://bkjws.sdu.edu.cn/b/cj/cjcx/xs/lscx', data=config.aoData,
                                 headers=config.HEADERS)
        if response.status_code == 200 and 'success' in response.text:
            return json.loads(response.text)
        return None
    except RequestException:
        return None

def parse_json(score_json):
    """解析成绩json，迭代每一科成绩，yield一个长str"""
    sub_aaData = score_json['object']['aaData']
    for item in sub_aaData:
        yield {
            "学年学期": item['xnxq'],
            "课程名": item['kcm'],
            # "教师名": item['jsm'],
            "课程属性": item['kcsx'],
            "学分": item['xf'],
            "最终成绩": item['kscjView'],
            "评分": item['wfzdj'],
            "绩点": item['wfzjd'],
            "期末成绩": item['qmcj'],
            "平时成绩": item['pscj'],
        }

def get_scores():
    score_now_json = get_now_score()
    score_past_json = get_past_score()
    scores = list(parse_json(score_now_json))
    scores.extend(iter(parse_json(score_past_json)))
    scores.sort(key=lambda x: x['学分'], reverse=True)
    return scores

def cal_GPA(scores, xnxq):
    """计算绩点"""
    GPA = 0.0
    sum_credits = 0.0
    for score in scores:
        if score["学年学期"] == xnxq:
            sum_credits += float(score["学分"])
            GPA += float(score["学分"]) * float(score["绩点"])
    return str(GPA / sum_credits) if sum_credits != 0 else '0.0'
