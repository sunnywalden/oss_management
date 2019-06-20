# !/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import qiniu
import os
import requests
import sys

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(BASE_DIR)

from utils.get_logger import Log
from conf import config
from utils.fonts_scanner import get_fonts_from_local


class QiniuManager:
    def __init__(self):
        log = Log()
        self.logger = log.logger_generate('qiniu_manage')
        self.auth = self.get_auth()

    def get_auth(self):
        auth = qiniu.Auth(config.qiniu_accesskeyid, config.qiniu_accesskeysecret)
        return auth

    def print_fonts(self, keyword='', pref='', prefix=config.qiniu_fonts_prefix):
        fonts_object_list = self.get_fonts(keyword=keyword, pref=pref, prefix=prefix)
        fonts_list = list(map(lambda font_object: font_object['key'].split(prefix)[-1], fonts_object_list))

        self.logger.info('Fonts found in qiniu %s' % fonts_list)
        print(fonts_list)

    def get_fonts(self, keyword='', pref='', prefix=config.qiniu_fonts_prefix):
        bucket = qiniu.BucketManager(self.auth)
        ret, eof, info = bucket.list(config.qiniu_fonts_bucket, prefix)

        fonts_object_list = list(filter(lambda font_info: font_info['key'].startswith(prefix) and keyword in font_info['key'] and ''.join(font_info['key'].split(prefix)[-1]).startswith(pref), ret['items']))
        # fonts_list = list(map(lambda font_info: font_info['key'].split(config.qiniu_fonts_prefix)[1], ret['items']))
        self.logger.info('There was %s fonts matched in qiniu' % len(fonts_object_list))
        print('There was %s fonts matched in qiniu' % len(fonts_object_list))
        # print(fonts_object_list)

        return fonts_object_list

    def download_fonts(self, keyword='', pref='', prefix=config.qiniu_fonts_prefix):
        fonts_list = self.get_fonts(keyword=keyword, pref=pref, prefix=prefix)

        for fonts_file in fonts_list:
            # private_url = self.auth.private_download_url(config.qiniu_domain + '/' + pref + fonts_file)
            font_name = fonts_file['key'].split(prefix)[-1]
            font_url = config.qiniu_domain + '/' + fonts_file['key']
            private_url = self.auth.private_download_url(font_url)
            print('Start to download resourse %s' % font_url)
            self.logger.info('Start to download resourse %s' % font_url)
            res = requests.get(private_url)
            assert res.status_code == 200
            font_file = res.content
            storage_path = os.path.join(BASE_DIR, config.qiniu_download_url)
            # print(storage_path)
            font_path = os.path.join(storage_path, font_name)
            # print(font_path)
            with open(font_path, 'wb') as f:
                f.write(font_file)
            self.logger.info('Fonts %s download success' % fonts_file)

    def upload_fonts(self, prefix=config.qiniu_fonts_prefix):
        fonts_list = get_fonts_from_local()
        bucket_name = config.qiniu_fonts_bucket

        for fonts_file in fonts_list:
            font_name = prefix + fonts_file.split('/')[-1]
            token = self.auth.upload_token(bucket=bucket_name, key=font_name)

            print(font_name)
            print(fonts_file)
            self.logger.info('Start to upload fonts %s' % fonts_file)
            res, info = qiniu.put_file(token, font_name,
                                       fonts_file)
            print(res, info)
            assert info.status_code == 200
            self.logger.info('Fonts %s upload success' % fonts_file)

    def delete_fonts(self, keyword='', pref='', prefix=config.qiniu_fonts_prefix):
        fonts_list = self.get_fonts(keyword=keyword, pref=pref, prefix=prefix)
        delete_fonts_object = list(
            filter(lambda fonts_file: keyword in fonts_file['key'] and fonts_file['key'].split(prefix)[-1].startswith(pref),
                   fonts_list))
        delete_fonts = list(map(lambda font_object: font_object['key'], delete_fonts_object))

        if not delete_fonts:
            print('No fonts matched for delete in qiniu fonts bucket')
        else:
            print('Fonts to be deleted %s' % delete_fonts)
            self.logger.info('Fonts to be deleted %s' % delete_fonts)

            bucket = qiniu.BucketManager(self.auth)
            ops = qiniu.build_batch_delete(config.qiniu_fonts_bucket, delete_fonts)
            res, info = bucket.batch(ops)

            print(res, info)
            assert info.status_code == 200
            print('Fonts %s delete success' % delete_fonts)
            self.logger.info('Fonts %s delete success' % delete_fonts)


if __name__ == '__main__':

    bucket_region = 'shanghai'
    # if you are not in a aliyun env, please set it to False
    inter_net = False

    bk_manage = QiniuManager()

    # print all fonts in ali oss font_dir
    bk_manage.print_fonts(keyword='AlibabaSans', pref='AlibabaSans')

    # # download all fonts from to local dir ./downloads/
    # bk_manage.download_fonts(keyword='AlibabaSans', pref='AlibabaSans')

    # upload all fonts in local dir ./fonts/
    # bk_manage.upload_fonts()

    # delete all fonts have keyword
    # bk_manage.delete_fonts(keyword='test', pref='test')
