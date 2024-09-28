import logging
import os

import arrow

from setting import LOGGING_FILENAME


# 创建自定义logger类
class Logger(logging.Logger):
    def __init__(self, name: str, business_date=arrow.now().format('YYYY-MM-DD')):
        super().__init__(name)
        logging_filename = LOGGING_FILENAME + business_date + '.log'
        file_handler = logging.FileHandler(logging_filename)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s %(name)-12s :%(levelname)-8s %(message)s',
                                           datefmt='%y-%m-%d %H:%M')
        file_handler.setFormatter(file_formatter)
        self.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-8s :: %(message)s',
                                              datefmt='%y-%m-%d %H:%M:%S')
        console_handler.setFormatter(console_formatter)
        self.addHandler(console_handler)


logger = Logger(os.getlogin())

if __name__ == '__main__':
    logger = Logger(os.getlogin())
    logger.debug('debug 测试')
    logger.info('info 测试')
    logger.warning('warning 测试')
    logger.error('error 测试')
    pass
