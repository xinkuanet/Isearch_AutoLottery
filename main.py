#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'

import datetime
import time
import os
import random
import re
import json
import logging
import sys
import requests
from requests_toolbelt import MultipartEncoder

from tools import encrypt_sign, getdate, get_MD5

requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5


class I_Studio(object):
    """
    艺赛旗设计器活动签到、抽奖
    """

    def __init__(self, username, password):
        """
        uername：艺赛旗用户名
        password: 密码
        """
        logger.info('-' * 5 + '艺赛旗设计器登录' + '-' * 5)
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
            logger.info('登录失败，错误信息：%s' % result.json().get('msg'))
        else:
            logger.info('登录成功，响应token结果：%s' % result.json().get('access_token'))
            self._access_token = result.json().get('access_token')

            # 生成抽奖页面链接
            url = 'https://rpa.i-search.com.cn/store/attendance?token=' + self._access_token + '&lang=zh_CN&machineCode=' + \
                  self._deviceCode + '&channel_no=DevStand&_=' + str(round(time.time() * 1000))
            logger.info('生成签到抽奖页面链接：%s' % url)

            # 第二步，获取用户信息结果
            url = 'https://account.i-search.com.cn/v1/studio/expiration?token=' + self._access_token + '&lang=zh_CN'
            result = self._session.get(url=url, verify=False)
            logger.info('用户最近登录时间：%s' % result.json().get('result').get('lastLoginTime'))
            self._custNo = result.json().get('result').get('custNo')
            self._custName = result.json().get('result').get('userName')
            self._tenantNo = result.json().get('result').get('tenantNo')

    def checkinHistroy(self):
        # 爬取签到历史，返回待签到日期
        logger.info('-' * 5 + '获取签到信息' + '-' * 5)
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
        if result.json().get('result'):
            # 存在签到历史，则判断签到历史
            day = result.json().get('result').get('day')
            signTimeList = [signDate.get('signTime') for signDate in result.json().get('result').get('signList')]
            logger.info('今天是签到周期中的第：%s 天，本周期已签到记录：%s' % (day, str(signTimeList)))
            # 获取最近三天日期
            dateFor3 = [getdate(day) for day in range(3 if int(day) > 3 else int(day))]
            # 获取最近三天还没签到的数据
            needCheckDate = [day for day in dateFor3 if day not in signTimeList]
            return needCheckDate
        else:
            # 无签到历史，则返回今天日期
            return [getdate(0)]

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
        logger.info('签到日期：%s，签到请求结果：%s' % (signTime, result.json().get('msg')))

    def lotterycount(self):
        """
        检查可签到次数
        :return: int
        """
        logger.info('-' * 5 + '获取可抽奖次数' + '-' * 5)
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
        logger.info('当前可抽奖次数为：%s' % remainingTimes)
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
            logger.info('抽奖抽到的奖品是：%s' % priceInfo)
            # 记录中奖奖品信息到本地文件
        else:
            logger.info('抽奖请求失败，请求结果：%s' % result.text)

    def __del__(self):
        # 关闭session连接
        self._session.close()


class I_Support(object):
    """
    艺赛旗社区发帖、删帖（目的是为了延迟设计器使用）
    """

    def __init__(self, username, password):
        """
        TODO： 登录
        :param username:用户名
        :param password: 密码
        """
        logger.info('-' * 5 + '艺赛旗社区登录' + '-' * 5)
        self._username = username
        self._password = password
        parme = {
            "nameOrEmail": self._username,
            "userPassword": get_MD5(self._password),
            "rememberLogin": True,
            "captcha": ""
        }
        self._session = requests.Session()
        self._session.keep_alive = False
        result = self._session.post('https://support.i-search.com.cn/login', data=str(parme), timeout=10, verify=False)
        if result.json().get('token'):
            logger.info('社区登录成功！')
            self._token = result.json().get('token')
        else:
            logger.info("社区登录失败！失败原因：%s" % result.json().get('msg'))

    def getCsrftoken(self):
        """
        获取 csrftoken
        """
        logger.info('-' * 5 + '开始获取csrfToken' + '-' * 5)
        url = 'https://support.i-search.com.cn/post?type=0'
        result = self._session.get(url=url, verify=False)  # 模拟请求获取网页信息
        csrftoken = re.findall(r"csrfToken: \'(.+?)\'", result.text)[0]  # 正则表达式提取csrftoken
        # 判断csrftoken是否存在
        if csrftoken:
            logger.info('获取成功！csrftoken：%s' % csrftoken)
            return csrftoken
        else:
            raise Exception("获取csrfToken失败：取消发帖！")

    def article(self, csrftoken, title, content):
        """
        发帖
        :param title:帖子标题
        :param content: 帖子内容
        :param csrftoken:
        :return: articleId 帖子id
        """
        logger.info('-' * 5 + '开始进行发帖' + '-' * 5)
        url = 'https://support.i-search.com.cn/article'
        headers = {
            "csrftoken": csrftoken,
            "Referer": "https://support.i-search.com.cn/post?type=0"
        }
        data = {
            "articleTitle": title,  # 文章标题
            "articleContent": content,  # 文章内容
            "articleTags": "疯狂吐槽,",  # 文章标签
            "articleCommentable": False,  # 是否允许回帖
            "articleType": 0,  # 文章类型，0：普通帖子，1：讨论组（小黑屋），2：同城广播，3：思绪
            "articleRewardContent": "",
            "articleRewardPoint": "",

        }

        data = json.dumps(data)  # 转换为字符串
        data = data.replace(' ', '')  # 去除空格，如不去除空格会提示：调用凭证不合法

        result = self._session.post(url=url, headers=headers, data=data, verify=False)
        if result.json().get('sc') == 0:
            articleId = result.json().get('articleId')
            logger.info('帖子发布成功！articleId：%s' % articleId)
            return articleId
        else:
            raise Exception('帖子发布失败，结束程序')

    def article_remove(self, articleId):
        """
        删除帖子
        :param articleId 帖子id
        :return:
        """
        # 删除帖子
        logger.info('-' * 5 + '开始进行删帖' + '-' * 5)
        url = 'https://support.i-search.com.cn/article/' + articleId + '/remove'
        result = self._session.post(url=url)
        if result.json().get('sc') == 0:
            logger.info('帖子删除成功！articleId：%s' % articleId)
        else:
            raise Exception('帖子删除失败，请手动社区进行删帖！')

    def __del__(self):
        # 关闭session连接
        self._session.close()


def getLogger(filename='isearch.md'):
    """
        日志记录、输出控制台
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 2、创建一个handler，用于写入日志文件
    fh = logging.FileHandler(filename=filename, mode='w', encoding='UTF-8')
    fh.setLevel(logging.INFO)
    fh_formatter = logging.Formatter('- %(message)s  ')
    fh.setFormatter(fh_formatter)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(ch_formatter)

    # 5、给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def sendMessage(key):
    """
    发送微信通知
    """
    with open('isearch.md', encoding='utf-8') as f:
        date = {'text': '艺赛旗自动签到通知',
                'desp': f.read()}
        url = 'https://sc.ftqq.com/' + key + '.send'
        result = requests.post(url, date)
        result.encoding = 'utf-8'
        if result.json().get('errno') == 0:
            logger.info('已发起微信推送！推送提示：%s' % str(result.json().get('errmsg')))


if __name__ == "__main__":
    # 1、创建一个logger
    logger = getLogger()
    env_dist = os.environ
    username = env_dist.get('USERNAME')  # 用户名
    password = env_dist.get('PASSWORD')  # 密码
    serverkey = env_dist.get('SERVERPUSHKEY')

    logger.info('当前时间：%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info('当前操作账户：%s' % username)
    if not all((username, password)):
        logger.info('请先从Actions secrets配置用户名及密码，再启动本流程！')
    else:
        # 设计器签到、抽奖
        studio = I_Studio(username, password)
        if studio._access_token:  # 登录成功进行后续操作
            needCheckDate = studio.checkinHistroy()  # 获取本周期待签到日期
            if needCheckDate:
                logger.info('需进行签到日期：%s' % str(needCheckDate))
                logger.info('-' * 5 + '开始进行签到' + '-' * 5)
                for day in needCheckDate:
                    # 进行签到
                    studio.checkin(signTime=day)
                    time.sleep(random.randint(1, 2))
            else:
                logger.info('无需签到日期，跳过签到动作！')

            remainingTimes = studio.lotterycount()
            if remainingTimes:
                logger.info('-' * 5 + '开始进行抽奖' + '-' * 5)
                for _ in range(remainingTimes):
                    studio.lottery()
                    time.sleep(random.randint(1, 2))
            else:
                logger.info('无可抽奖次数，跳过抽奖动作！')

        # 社区发帖、删帖
        community = I_Support(username, password)
        if community._token:  # 判断是否登录成功
            try:
                csrftoken = community.getCsrftoken()
                title = '延迟设计器使用' + str(random.random())
                content = """大哥大嫂过年好，本帖仅用于延长一天设计器使用，发完即删!
如您有幸看到本帖，祝福您在新的一年里:
事业正当午,身体壮如虎,金钱不胜数,干活不辛苦,悠闲像老鼠, 浪漫似乐谱,快乐莫你属!
感谢！！共建美好文明社区！"""
                articleId = community.article(csrftoken, title, content)
                community.article_remove(articleId)
            except Exception as e:
                logger.info(e)

    # 微信通知
    if serverkey:
        sendMessage(serverkey)
    else:
        logger.info('未开启Server酱推送，不进行微信通知！')
