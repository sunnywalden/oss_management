#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: sunnywalden@gmail.com

import os
from utils.get_logger import Log


def get_fonts_from_local():
    log = Log()
    logger = log.logger_generate('font_scanner')

    # fonts_lists = []
    for root, dirs, files in os.walk('../fonts'):
        logger.info('File found %s, dirs: %s' % (files, dirs))
        for file in files:
            logger.info('File found %s' % file)
            fonts_file_path = os.path.join(root, file)
            if os.path.splitext(file)[1] == '.ttf' or os.path.splitext(file)[1] == '.otf':
                # fonts_lists.append(os.path.join(root, file))

                logger.info('Fonts file found: %s' % fonts_file_path)
                yield fonts_file_path
            else:
                logger.info('Files which is not a fonts be ignored: %s' % file)

    # logger.info('Fonts gonna to be uploaded are: %s' % fonts_lists)
    # return fonts_lists


if __name__ == '__main__':

    get_fonts_files = get_fonts_from_local()
    for fonts_file in iter(get_fonts_files):
        print(fonts_file)

