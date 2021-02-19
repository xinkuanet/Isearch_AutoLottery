# !/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'

import logging

# logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s',
#                     filename='test.log', filemode='w')
#
#
# # sys.stdout
# logging.debug('debug message')
# logging.info('info message')
# logging.warning('warning message')
# logging.error('error message')
# logging.critical('critical message')
# print('')


############################################

import logging

# 创建一个logger日志对象
import sys





import logging

# 1、创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 2、创建一个handler，用于写入日志文件
fh = logging.FileHandler('test.log')
fh.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)

# 3、定义handler的输出格式（formatter）
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 4、给handler添加formatter
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 5、给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)
logger.debug(msg='ddd')


