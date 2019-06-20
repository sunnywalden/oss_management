# !/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import oss2
import json
import base64
import os
import sys
import time
from itertools import islice
import argparse

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from utils.get_logger import Log
from utils.fonts_scanner import get_fonts_from_local
from conf import config
from aliOss.oss_manage import OssManager
from aliOss.bucket_manage import BucketManager

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='python ali_fonts_manage.py [--action [action]] [--fonts_list [fonts_list]]',
                                     description='Manage ali oss storage of ai fonts')
    parser.add_argument('--action', default='print', type=str, dest='action', choices=['print', 'download', 'upload', 'delete'],
                        help="what to do with fonts, print download or upload and delete "
                                                          "(default: print)")
    parser.add_argument('--fonts_list', default='', type=str, dest='fonts',
                        help="fonts list that wanna to be deleted, separated by comma, "
                                                         "like test.ttf,test1.ttf(default: '')")

    bucket_region = 'shanghai'
    # if you are not in a aliyun env, please set it to False
    inter_net = False

    bk_manage = BucketManager(internet=inter_net)

    if len(sys.argv) < 2:
        parser.print_help()
    elif len(sys.argv) == 2:
        print(sys.argv[1])
        args = parser.parse_args(['--action', sys.argv[1]])
        if args['action'] == 'print':

            # print all fonts in ali oss font_dir
            bk_manage.print_fonts()
        elif args['action'] == 'download':
            # # download all fonts from to local dir ./downloads/
            bk_manage.download_fonts()
        elif args['action'] == 'upload':
            # upload all fonts in local dir ./fonts/
            bk_manage.upload_fonts_files()
    else:
        args = parser.parse_args(['--action', sys.argv[1], '--fonts_list', sys.argv[2]])
        fonts_str = args['fonts']
        fonts_list = fonts_str.split(',')
        bk_manage.delete_fonts(fonts_list)
