#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: sunnywalden@gmail.com

import logging
import socket
from logging.handlers import RotatingFileHandler
import os
import time


class Log(object):
    def __init__(self):
        self.logger = logging.getLogger('log')

    def logger_generate(self, name):
        # log_level = logging[level]
        # try:
        #     log_level = logging['INFO']
        #     print('debug log level %s' % log_level)
        #     self.logger.setLevel(log_level)
        #
        # except Exception, e:
        #     self.logger.info('Logger init failed %s' % e)
        # log_level = 'logging.INFO'

        self.logger.setLevel(logging.INFO)

        unix_time = time.time()
        # d_time = time.strftime()

        log_file = os.path.join('../logs', name + '.log')

        # print('generate log file %s' % log_file)
        handler = RotatingFileHandler(filename=log_file, mode='a', encoding='utf-8', maxBytes=1024 * 1024,
                                      backupCount=3)
        # if os.path.isfile(log_file):
        # print('log file %s generate successful' % os.path.abspath(log_file))
        #        else:

        formatter = logging.Formatter(
            fmt='%(asctime)s %(process)d %(levelname)s %(thread)d - %(funcName)s %(filename)s:%(lineno)d %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        socket.setdefaulttimeout(10)

        return self.logger