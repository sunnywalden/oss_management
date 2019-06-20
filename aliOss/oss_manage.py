# !/usr/bin/env python
# coding=utf-8
# author: sunnywalden@gmail.com

import oss2
from utils.get_logger import Log
from conf import config


class OssManager:
    def __init__(self):
        log = Log()
        self.logger = log.logger_generate('oss_manage')
        self.auth = self.get_auth()


    @staticmethod
    def get_auth():
        auth = oss2.Auth(config.ali_accesskeyid, config.ali_accesskeysecret)
        return auth

    def get_oss_url(self, region, internal_net=True):
        if internal_net:
            oss_url = 'http://oss-cn-' + region.lower() + '-internal.aliyuncs.com'
        else:
            oss_url = 'http://oss-cn-' + region.lower() + '.aliyuncs.com'
        self.logger.info('Oss url of region %s: %s' % (region, oss_url))
        return oss_url

    def get_bucket_list(self, region, prefix='', internal_net=True):
        oss_url = self.get_oss_url(region, internal_net)
        oss_service = oss2.Service(self.auth, oss_url, )
        bucket_lists = oss_service.list_buckets(prefix=prefix)
        self.logger.info('Bucket list of region %s:' % region)

        return bucket_lists

    def get_fonts_bucket(self, oss_url, ):
        bucket = oss2.Bucket(self.auth, oss_url, )

        return bucket


if __name__ == '__main__':
    oss_manage = OssManager()

    bucket_region = 'shanghai'
    inter_net = False

    bucket_list = oss_manage.get_bucket_list(bucket_region, internal_net=inter_net)
    oss_manage.logger.info('Bucket lists of %s: %s' % (bucket_region, bucket_list))



