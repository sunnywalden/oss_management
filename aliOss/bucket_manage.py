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

from utils.get_logger import Log
from utils.fonts_scanner import get_fonts_from_local
from conf import config
from aliOss.oss_manage import OssManager


class BucketManager:
    def __init__(self, internet=True):
        log = Log()
        self.logger = log.logger_generate('bucket_manage')
        self.auth = self.get_auth()
        # self.region = region
        self.inter_net = internet
        # self.buck_name = bucket_name

    @staticmethod
    def get_auth():
        auth = oss2.Auth(config.ali_accesskeyid, config.ali_accesskeysecret)
        return auth

    def create_bucket(self, region, bucket_name):
        oss_url = OssManager.get_oss_url(region, internal_net=False)
        bucket = oss2.Bucket(self.auth, oss_url, bucket_name)

        # 设置存储空间为私有读写权限。
        bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)

    def get_font_bucket(self):
        oss_manager = OssManager()

        for font_bucket_region in config.ali_fonts_bucket:
            region = font_bucket_region
            font_oss_url = oss_manager.get_oss_url(region, internal_net=self.inter_net)
            bucket_name = config.ali_fonts_bucket[font_bucket_region]['bucket_name']
            font_bucket = oss2.Bucket(self.auth, font_oss_url, bucket_name)
            yield font_bucket

    def percentage(self, consumed_bytes, total_bytes):
        """进度条回调函数，计算当前完成的百分比

        :param consumed_bytes: 已经上传/下载的数据量
        :param total_bytes: 总数据量
        """
        if total_bytes:
            # time.sleep(30)
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            if rate != 0 and rate % 25 == 0 or rate % 50 == 0 or rate % 75 == 0 or rate % 100 == 0:
                print(' {0}% '.format(rate), end=' ')
            sys.stdout.flush()

    def upload_fonts(self, file_path):
        file_name = file_path.split('/')[-1]

        fonts_buckets = self.get_font_bucket()
        for fonts_bucket in fonts_buckets:

            # get bucket region
            fonts_bucket_info = fonts_bucket.get_bucket_info()
            region = fonts_bucket_info.location.split('-')[-1]
            # get font bucket sotorage dir
            fonts_dir = config.ali_fonts_bucket[region]['font_dir']

            upload_res = oss2.resumable_upload(fonts_bucket, os.path.join(fonts_dir, file_name), file_path,
                                               store=oss2.ResumableStore(root='./tmp_files/uploads'),
                                               multipart_threshold=100 * 1024,
                                               part_size=100 * 1024,
                                               progress_callback=self.percentage,
                                               num_threads=4)
            print('', end='\n')
            # print('Upload response: %s' % upload_res)
            if upload_res.status == 200 or upload_res.resp.status == "OK":
                print('Font %s upload to bucket %s successed' % (file_name, fonts_bucket.bucket_name))
                self.logger.info('Font %s upload to bucket %s successed' % (file_name, fonts_bucket.bucket_name))
            else:
                print('Font %s upload to bucket %s failed' % (file_name, fonts_bucket.bucket_name))
                self.logger.error('Font %s upload to bucket %s failed' % (file_name, fonts_bucket.bucket_name))

    def delete_fonts(self, files_names=[], keyword='', pref=''):

        fonts_buckets = self.get_font_bucket()
        for fonts_bucket in fonts_buckets:

            # get bucket region
            fonts_bucket_info = fonts_bucket.get_bucket_info()
            region = fonts_bucket_info.location.split('-')[-1]
            bucket_name = config.ali_fonts_bucket[region]['bucket_name']
            # get font bucket sotorage dir
            fonts_dir = config.ali_fonts_bucket[region]['font_dir']

            if files_names:
                fonts_list = list(map(lambda file_name: os.path.join(fonts_dir, file_name), files_names))
            else:
                fonts_dict = self.get_fonts(keyword=keyword, pref=pref)
                # print(fonts_dict)
                if fonts_dict:

                    fonts_list = fonts_dict[bucket_name]
                else:
                    fonts_list = []
                    print('No fonts matched to be deleted in bucket %s' % bucket_name)
                    self.logger.info('No fonts matched to be deleted in bucket %s' % bucket_name)
                    break
            if fonts_list:
                fonts_names = list(map(lambda font_oss_object: font_oss_object.key, fonts_list))
                print(fonts_names)
                print('Fonts %s to be deleted in bucket %s' % (fonts_names, bucket_name))
                self.logger.info('Fonts %s to be deleted in bucket %s' % (fonts_names, bucket_name))
                delete_res = fonts_bucket.batch_delete_objects(fonts_names)
                print('Delete response: %s' % delete_res)
                self.logger.info('Delete response: %s' % delete_res)
                if delete_res.status == 200 or delete_res.resp.status == "OK":
                    self.logger.info(
                        'Font %s delete from bucket %s successed' % (delete_res.deleted_keys, fonts_bucket.bucket_name))
                else:
                    self.logger.error(
                        'Font %s delete from bucket %s failed' % (delete_res.deleted_keys, fonts_bucket.bucket_name))
            else:
                pass

    def get_fonts(self, keyword='', pref=''):

        fonts_dict = {}
        for fonts_bucket in iter(self.get_font_bucket()):
            # get bucket region
            fonts_bucket_info = fonts_bucket.get_bucket_info()
            region = fonts_bucket_info.location.split('-')[-1]

            # get font bucket sotorage dir
            fonts_dir = config.ali_fonts_bucket[region]['font_dir']

            self.logger.info('Fonts storage direction %s' % fonts_dir)

            fonts_list_object = fonts_bucket.list_objects(prefix=fonts_dir, max_keys=1000)
            fonts_list = fonts_list_object.object_list
            fonts_names = list(filter(
                lambda fonts_name: keyword in fonts_name.key and fonts_name.key.split(fonts_dir)[-1].startswith(pref),
                fonts_list))

            fonts_dict[fonts_bucket.bucket_name] = fonts_names

        return fonts_dict

    def print_fonts(self, keyword='', pref=''):

        fonts_dict = self.get_fonts(keyword=keyword, pref=pref)
        print(fonts_dict)

        # for bucket_name, fonts_list in fonts_dict:
        for bucket_name in fonts_dict:
            fonts_list = fonts_dict[bucket_name]

            print('There is total %s Fonts in bucket：%s ' % (len(fonts_list), bucket_name))
            self.logger.info('Fonts in bucket : %s ' % bucket_name)

            for font in fonts_list:
                file_name = font.key
                if file_name.endswith('tf'):
                    print('%s' % file_name)
                    self.logger.info('%s' % file_name)

    def download_fonts(self, keyword='', pref=''):

        for fonts_bucket in iter(self.get_font_bucket()):
            # get bucket region
            fonts_bucket_info = fonts_bucket.get_bucket_info()
            region = fonts_bucket_info.location.split('-')[-1]

            # get font bucket sotorage dir
            fonts_dir = config.ali_fonts_bucket[region]['font_dir']
            bucket_name = fonts_bucket.bucket_name

            # oss2.ObjectIteratorr用于遍历文件。
            oss_object_list = oss2.ObjectIterator(fonts_bucket)

            for font_file in oss_object_list:
                file_name = font_file.key.split(fonts_dir)[-1]
                if file_name.endswith('tf') and keyword in file_name and file_name.startswith(pref) and fonts_dir in font_file.key:
                    print('fonts %s matched for download in bucket %s' % (font_file.key, fonts_bucket.bucket_name))
                    self.logger.info(
                        'fonts %s matched for download in bucket %s' % (font_file.key, fonts_bucket.bucket_name))

                    try:
                        oss2.resumable_download(fonts_bucket, font_file, '../downloads/' + font_file,
                                                part_size=100 * 1024,
                                                num_threads=3,
                                                progress_callback=self.percentage,
                                                store=oss2.ResumableDownloadStore(root='./tmp_files/downloads'))
                    except oss2.exceptions.NotFound as en:
                        self.logger.exception('Font %s not found while download fonts' % font_file)
                    except Exception as e:
                        self.logger.exception('Exception catched while download fonts %s: %s' % (font_file, e))
                else:
                    # print('fonts %s not matched for download in bucket %s' % (file_name, fonts_bucket.bucket_name))
                    self.logger.debug('fonts %s not matched for download in bucket %s' % (file_name, fonts_bucket.bucket_name))

    def upload_fonts_files(self):
        get_fonts_files = get_fonts_from_local()
        for fonts_file in iter(get_fonts_files):
            print('Fonts to be uploaded to ali oss: %s' % fonts_file)
            self.logger.info('Fonts to be uploaded to ali oss: %s' % fonts_file)
            self.upload_fonts(fonts_file)


if __name__ == '__main__':
    bucket_region = 'shanghai'
    # if you are not in a aliyun env, please set it to False
    inter_net = False

    bk_manage = BucketManager(internet=inter_net)

    # print all fonts in ali oss font_dir
    bk_manage.print_fonts(keyword='AlibabaSans', pref='AlibabaSans')

    # # download all fonts from to local dir ./downloads/
    # bk_manage.download_fonts(keyword='test', pref='test')
    # bk_manage.download_fonts(keyword='AlibabaSans', pref='AlibabaSans')

    # upload all fonts in local dir ./fonts/
    # bk_manage.upload_fonts_files()

    # bk_manage.delete_fonts(keyword='test', pref='test')
