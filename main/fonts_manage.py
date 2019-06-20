# !/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import argparse
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from qiniuOss.qiniu_fonts_manage import QiniuManager
from aliOss.bucket_manage import BucketManager
from utils.get_logger import Log

if __name__ == '__main__':

    log = Log()

    logger = log.logger_generate('fonts_manage')

    parser = argparse.ArgumentParser(usage='python ali_fonts_manage.py [--action [action]] [--keyword [keyword]]',
                                     description='Manage ali oss storage of ai fonts')
    parser.add_argument('--action', default='print', type=str, dest='action', choices=['print', 'download', 'upload', 'delete'],
                        help="what to do with fonts, print download or upload and delete "
                                                          "(default: print)")
    parser.add_argument('--keyword', default='', type=str, dest='keyword',
                        help="keyword for search fonts in bucket, "
                                                         "like SourceHan(default: '')")
    parser.add_argument('--prefix', default='', type=str, dest='prefix',
                        help="prefix for search fonts in bucket, "
                                                         "like AlibabaSans(default: '')")

    args = parser.parse_args()

    print(args)

    bucket_region = 'shanghai'
    # if you are not in a aliyun env, please set it to False
    inter_net = False

    ali_bk_manage = BucketManager(internet=inter_net)
    qiniu_bk_manage = QiniuManager()

    fonts_action = args.action
    fonts_keyword = args.keyword
    fonts_prefix = args.prefix

    if fonts_action == 'print':
        # print all fonts in ali oss font_dir
        ali_bk_manage.print_fonts(keyword=fonts_keyword, pref=fonts_prefix)
        qiniu_bk_manage.print_fonts(keyword=fonts_keyword, pref=fonts_prefix)
    elif fonts_action == 'download':
        # # download all fonts from to local dir ./downloads/
        ali_bk_manage.download_fonts(keyword=fonts_keyword, pref=fonts_prefix)
        qiniu_bk_manage.download_fonts(keyword=fonts_keyword, pref=fonts_prefix)
    elif fonts_action == 'upload':
            # upload all fonts in local dir ./fonts/
        ali_bk_manage.upload_fonts_files()
        qiniu_bk_manage.upload_fonts()
    elif fonts_action == 'delete':
        args = parser.parse_args(['--action', sys.argv[1], '--keyword', sys.argv[2]])
        fonts_keyword = args['keyword']
        ali_bk_manage.delete_fonts(keyword=fonts_keyword, pref=fonts_prefix)
        qiniu_bk_manage.delete_fonts(keyword=fonts_keyword, pref=fonts_prefix)
    else:
        logger.info('Wrong action passed, choose print instead')
        ali_bk_manage.print_fonts(keyword=fonts_keyword, pref=fonts_prefix)
        qiniu_bk_manage.print_fonts(keyword=fonts_keyword, pref=fonts_prefix)




