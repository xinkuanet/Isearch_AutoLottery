#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'
import hmac
import base64
import datetime
from urllib import parse
import hashlib

def encrypt_sign(timestamp, data='', key='isearch'):
    """对请求数据、时间戳进行 HmacSHA256、base64 加密，得到签名"""
    if data:
        timestamp = data + '&' + "timestamp=" + timestamp  # 拼接要加密的签名
    else:
        timestamp = "timestamp=" + timestamp  # 要加密的内容
    timestamp = parse.quote(timestamp)  # 对内容进行URL编码
    # 特殊字符串替换，省略。。。。
    sha256_str = hmac.new(bytes(key, encoding='utf-8'), bytes(timestamp, encoding='utf-8'),
                          digestmod=hashlib.sha256).digest()
    hex_str = sha256_str.hex()
    signature = bytes.decode(base64.b64encode(hex_str.encode('utf-8')))
    return signature

def getdate(self, beforeOfDay=0):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d')
    return re_date