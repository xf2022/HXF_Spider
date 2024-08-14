import collections
import importlib

import arrow

from image_sharing_webs.dao.common_db import MySqlSingleConnect
from image_sharing_webs.logger.common_logger import logger


class TaskWorker:
    def __init__(self, business_date=arrow.now().format("YYYY-MM-DD"), config=None, optimistic_lock=None):
        self.logger = logger
        self.db = MySqlSingleConnect()
        self.business_date = business_date
        self.config = config
        self.optimistic_lock = optimistic_lock
        pass

    def update_task_status(self, status):
        task_record_update_sql = "update task_record " \
                                 "set status = %s, exec_log = %s" \
                                 "where task_id = %s and optimistic_lock = %s;"
        if status == 3:
            result = self.db.exec_one(task_record_update_sql,
                                      (status, '任务进行中', self.config.task_id, self.optimistic_lock))
            self.logger.info('任务-{} 进行中'.format(self.config.task_name))
        elif status == 4:
            result = self.db.exec_one(task_record_update_sql,
                                      (status, '任务完成', self.config.task_id, self.optimistic_lock))
            self.logger.info('任务-{} 已完成'.format(self.config.task_name))
        else:
            result = self.db.exec_one(task_record_update_sql,
                                      (status, '任务出错', self.config.task_id, self.optimistic_lock))
            self.logger.error('任务-{} 出错'.format(self.config.task_name))
        if result > 0:
            return True
        else:
            return False

    def run(self):
        if self.config:
            try:
                self.update_task_status(3)
                self.logger.info('任务-{} 开始执行'.format(self.config.task_name))
                path_str = self.config.handle.split('.')
                module_str = '.'.join(path_str[:-1])
                class_str = path_str[-1]
                module = importlib.import_module(module_str)
                class_ = getattr(module, class_str)
                obj = class_()
                obj.run()
                self.update_task_status(4)
            except Exception as e:
                self.update_task_status(2)
                self.logger.error('任务-{} 出错'.format(self.config.task_name))
                self.logger.error(e)


def start_task(config, optimistic_lock):
    TaskWorker(config=config, optimistic_lock=optimistic_lock).run()


if __name__ == '__main__':
    TaskConfig = collections.namedtuple('config', ['task_id', 'handle'])
    config = TaskConfig(1, '测试.test.03_test_import.test_class.TestClass')
    start_task(config, 0)
    pass
