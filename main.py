#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'

import datetime
import json
import os
import random
import time

import requests
from requests_toolbelt import MultipartEncoder

from tools import encrypt_sign, getdate


requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5


class Is_checkin(object):
    def __init__(self, username, password):
        """
        uername：艺赛旗用户名
        password: 密码
        """
        print('-'*5 + '艺赛旗账户自动登录' + '-'*5)
        self._username = username  # 用户名
        self._password = password  # 密码
        self._deviceCode = ''.join(random.choice('0123456789ABCDEF') for _ in range(32))  # 生成随机机器码
        self._session = requests.Session()  # 创建Session
        self._session.keep_alive = False  # 关闭长连接
        # 第一步，获取token
        url = 'https://account.i-search.com.cn/oauth/token'
        fields = {
            'client_id': 'studio10001',
            'client_secret': 'clientSecret',
            'grant_type': 'studio',
            'password': password,
            'username': username,
            'lang': 'zh_CN'
        }
        self._me = MultipartEncoder(fields=fields)
        headers = {'Content-Type': self._me.content_type}
        result = self._session.post(url=url, data=self._me, headers=headers, verify=False)

        # '{"code":2021,"msg":"用户或者密码错误"}'
        #

        if not result.json().get('access_token'):
            print('登录失败，错误信息：%s' % result.json().get('msg'))
            exit()
        else:
            print('登录成功，响应token结果：%s' % result.json().get('access_token'))
            self._access_token = result.json().get('access_token')

            # 生成抽奖页面链接
            url = 'https://rpa.i-search.com.cn/store/attendance?token=' + self._access_token + '&lang=zh_CN&machineCode=' + \
                 self._deviceCode + '&channel_no=DevStand&_=' + str(round(time.time() * 1000))
            print('生成签到抽奖页面链接：%s' % url)

            # 第二步，获取用户信息结果
            url = 'https://account.i-search.com.cn/v1/studio/expiration?token=' + self._access_token + '&lang=zh_CN'
            result = self._session.get(url=url, verify=False)
            print('用户最近登录时间：%s' % result.json().get('result').get('lastLoginTime'))
            self._custNo = result.json().get('result').get('custNo')
            self._custName = result.json().get('result').get('userName')
            self._tenantNo = result.json().get('result').get('tenantNo')

    def checkinHistroy(self):
        # 获取签到历史
        print('-' * 5 + '获取签到信息' + '-' * 5)
        url = "https://restapi.i-search.com.cn/store/v1/checkin?custNo=" + self._custNo
        timestamp = str(round(time.time() * 1000))  # 获取时间戳
        signature = encrypt_sign(timestamp=timestamp, data='custNo=' + self._custNo)  # 计算签名
        headers = {
            "accesstoken": self._access_token,
            "content-type": "application/json; charset=UTF-8",
            "signature": signature,
            "tenantno": self._tenantNo,
            "timestamp": timestamp,
        }
        result = self._session.get(url=url, headers=headers, verify=False)  # 发送请求
        day = result.json().get('result').get('day')
        signTimeList = [signDate.get('signTime') for signDate in result.json().get('result').get('signList')]
        print('今天是签到周期中的第：%s 天，本周期已签到记录：%s' % (day, str(signTimeList)))
        return signTimeList

    def checkin(self, signTime=""):
        """
        签到
        :param signTime:签到日，为空则默认当天, '2020-06-24'
        :param signType:签到标志，正常签到为0，补签为1，设置补签扣100币
        :return:
        """
        if not signTime:  # 如果没指定签到日期，则默认签到日期为今天
            signTime = datetime.datetime.now().strftime('%Y-%m-%d')
            signType = 0
        elif signTime == datetime.datetime.now().strftime('%Y-%m-%d'):
            signType = 0
        else:
            signType = 1
        # signType = 1
        url = 'https://restapi.i-search.com.cn/store/v1/checkin/sava'
        data = {
            "tenantNo": self._tenantNo,
            "custNo": self._custNo,
            "machineCode": self._deviceCode,
            "signTime": signTime,  # 表示要签到的日期，正常可以补前两天，系统有bug，可以无限往前补签
            "signType": signType,  # 正常签到为0，补签为1，设置补签扣100币
            "channelNo": "DevStand"
        }
        data = json.dumps(data)  # 转换为字符串
        data = data.replace(' ', '')  # 去除空格，如不去除空格会提示：调用凭证不合法
        timestamp = str(round(time.time() * 1000))  # 获取时间戳
        signature = encrypt_sign(timestamp=timestamp, data=data)  # 计算签名
        headers = {
            "accesstoken": self._access_token,
            "content-type": "application/json; charset=UTF-8",
            "signature": signature,
            "tenantno": self._tenantNo,
            "timestamp": timestamp,
        }
        result = self._session.post(url=url, headers=headers, data=data)  # 发送签到请求
        print('签到日期：%s，签到结果：%s' % (signTime, result.text))


    def lotterycount(self):
        """
        检查可签到次数
        :return: int
        """
        print('-' * 5 + '获取可抽奖次数' + '-' * 5)
        # 第一步，统计账号可抽奖次数
        url = 'https://restapi.i-search.com.cn/store/v1/lotterycount?custNo=' + self._custNo
        timestamp = str(round(time.time() * 1000))  # 获取时间戳
        signature = encrypt_sign(timestamp=timestamp, data='custNo=' + self._custNo)  # 计算签名
        headers = {
            "accesstoken": self._access_token,
            "signature": signature,
            "timestamp": timestamp
        }
        # result = self._session.get(url=url, headers=headers)  # 发送请求
        result = self._session.get(url=url, headers=headers, verify=False)  # 发送请求
        remainingTimes = result.json()['result']['remainingTimes']  # 可抽奖次数
        print('当前可抽奖次数为：%s' % remainingTimes)
        return remainingTimes

    def lottery(self, pricedict='奖品信息字典.json'):
        """
        抽奖
        :param pricedict:   奖品字典文件路径
        :param lotterylog:  中奖文件日志路径
        :return:
        """
        # 开始进行抽奖

        url = 'https://restapi.i-search.com.cn/store/v1/lottery'  # 抽奖请求地址
        data = {
            "custNo": self._custNo,
            "tenantNo": self._tenantNo,
            "channelNo": "DevStand",
            "machineCode": self._deviceCode
        }
        data = json.dumps(data)  # 转换为字符串
        data = data.replace(' ', '')  # 去除空格，如不去除空格会提示：调用凭证不合法
        timestamp = str(round(time.time() * 1000))  # 获取时间戳
        signature = encrypt_sign(timestamp=timestamp, data=data)  # 计算签名
        headers = {
            "accesstoken": self._access_token,
            "content-type": "application/json; charset=UTF-8",
            "signature": signature,
            "tenantno": self._tenantNo,
            "timestamp": timestamp,
        }
        result = self._session.post(url=url, headers=headers, data=data)  # 发送抽奖请求
        if result.json()['msg'] == '操作成功':
            prizeId = result.json()['result']['id']  # 奖品id
            # 根据奖品id显示对应的奖品信息
            with open(pricedict, 'r', encoding='utf-8') as f:
                price_dict = f.read()
            price_dict = eval(price_dict)  # 字符串转换字典
            priceInfo = price_dict[str(prizeId)]  # 奖品信息
            print('抽奖抽到的奖品是：%s' % priceInfo)
            # 记录中奖奖品信息到本地文件
        else:
            print('抽奖请求失败，请求结果：%s' % result.text)

    def __del__(self):
        # 关闭session连接
        self._session.close()


if __name__ == "__main__":
    print('当前时间：', datetime.datetime.now())
    env_dist = os.environ
    username = env_dist.get('USERNAME')  # 用户名
    password = env_dist.get('PASSWORD')  # 密码
    if not all((username, password)):
        print('获取用户名密码失败，请从先配置用户名或密码再启动程序！')
        exit()
    isearch = Is_checkin(username, password)
    signTimeList = isearch.checkinHistroy()  # 获取本周期签到历史

    # 获取最近三天日期
    dateFor3 = [getdate(day) for day in range(3)]
    # 获取最近三天还没签到的数据
    needCheckDate = [day for day in dateFor3 if day not in signTimeList]
    if needCheckDate:
        print('需进行签到日期：%s' % str(needCheckDate))
        print('-' * 5 + '开始进行签到' + '-' * 5)
        for day in needCheckDate:
            # 进行签到
            isearch.checkin(signTime=day)
            time.sleep(random.randint(2, 4))
    else:
        print('无需签到日期，跳过签到动作！')

    remainingTimes = isearch.lotterycount()
    if remainingTimes:
        print('-' * 5 + '开始进行抽奖' + '-' * 5)
        for _ in range(remainingTimes):
            isearch.lottery()
            time.sleep(random.randint(2, 4))
    else:
        print('无可抽奖次数，跳过抽奖动作！')

