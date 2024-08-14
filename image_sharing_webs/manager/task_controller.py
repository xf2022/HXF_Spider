import collections
import os
import sys
import time
from multiprocessing import Process

import arrow

sys.path.append(r'D:\programme\python\HXF_Spider')

from image_sharing_webs.dao.common_db import MySqlSingleConnect
from image_sharing_webs.logger.common_logger import logger
from image_sharing_webs.manager.task_worker import start_task
from setting import PROCESS_COUNT

process_count = PROCESS_COUNT

TaskConfig = collections.namedtuple('config', ['task_id', 'task_name', 'handle', 'description'])


class GetTask:
    """
    获取任务
    """

    def __init__(self, business_date=arrow.now().format("YYYY-MM-DD")):
        self.logger = logger
        self.db = MySqlSingleConnect()
        self.business_date = business_date
        self.task_id = None
        self.task_name = None
        self.optimistic_lock = None

    def is_wait_for_task(self):
        query_task_record_sql = "select count(1) from task_record " \
                                "where business_date = '%s' and status in (0, 1, 2, 3, 5);"
        result = self.db.query_one(query_task_record_sql % self.business_date)
        if result[0]:
            return True
        else:
            return False

    def is_exists_task(self):

        task_record_sql = "select task_id, task_name, optimistic_lock from task_record " \
                          "where business_date = '{}' and status = 1 and exec_log = '任务生成';"

        result = self.db.query(task_record_sql.format(self.business_date))
        if len(result) > 0:
            self.task_id = result[0][0]
            self.task_name = result[0][1]
            self.optimistic_lock = result[0][2]
            return True
        else:
            return False

    def is_get_task(self):

        task_record_sql = "select task_id, task_name, optimistic_lock from task_record " \
                          "where business_date = '{}' and status = 1 and exec_log = '任务生成';"

        task_record_update_sql = "update task_record " \
                                 "set status = 2, exec_log = '任务已获取', optimistic_lock = optimistic_lock + 1 " \
                                 "where task_id = %s and optimistic_lock = %s"
        query_result = self.db.query(task_record_sql.format(self.business_date))
        if len(query_result):
            self.task_id, self.task_name, self.optimistic_lock = query_result[0]
            result = self.db.exec_one(task_record_update_sql, (self.task_id, self.optimistic_lock))
            if result > 0:
                self.optimistic_lock += 1
                return True
        self.task_id = self.optimistic_lock = None
        return False

    def get_task_config(self):
        task_config_sql = "select task_id, task_name, handle, description from task_config " \
                          "where task_id = {}".format(self.task_id)
        result = self.db.query_one(task_config_sql)
        if result:
            task_config = TaskConfig(result[0], result[1], result[2], result[3])
            return task_config
        else:
            return result

    def run(self):
        # 判断是否存在任务，如果存在任务则一直运行下去
        while self.is_wait_for_task() or '23:30' < arrow.now().format('HH:mm'):
            # 获取其中一个‘已生成的任务’
            if not self.is_get_task():
                time.sleep(60)
                continue
            self.logger.info('任务-{} 获取'.format(self.task_name))
            config = self.get_task_config()
            # 判断任务是否进行了配置
            if config:
                # 将任务交由task_worker执行
                start_task(config=config, optimistic_lock=self.optimistic_lock)
            else:
                self.logger.warning('任务-{} 未进行配置'.format(self.task_name))
        pass


def get_task():
    GetTask().run()


class TaskController:
    def __init__(self, business_date=arrow.now().format("YYYY-MM-DD")):
        self.logger = logger
        self.business_date = business_date

    def run(self):
        """
        获取任务，生成
        :return:
        """
        process_list = []

        for i in range(process_count):
            process = Process(target=get_task, name=f'取数进程_{i}')
            self.logger.info(f'开启取数进程_{i}')
            process_list.append(process)

        for process in process_list:
            process.start()
        for process in process_list:
            process.join()
        pass


if __name__ == '__main__':
    os.chdir(r'D:\programme\python\HXF_Spider')
    print(os.getcwd())
    TaskController().run()
