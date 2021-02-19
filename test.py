#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = '孙思锴'

import logging

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='test.log', filemode='a')



logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
logging.error('error message')
logging.critical('critical message')
