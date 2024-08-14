import os
import sys
import time

import arrow

sys.path.append(r'D:\programme\python\HXF_Spider')

from image_sharing_webs.dao.common_db import MySqlSingleConnect
from image_sharing_webs.logger.common_logger import logger


class TaskCreator:

    def __init__(self, business_date=None):
        self.db = MySqlSingleConnect()
        self.logger = logger
        if business_date:
            self.business_date = business_date
        else:
            self.business_date = arrow.now().format('YYYY-MM-DD')

    def __del__(self):
        self.db.close()

    # def __enter__(self):
    #     self.db = MySqlSingleConnect()
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.db.close()

    def get_task_list(self):
        task_list = []
        select_task_schedule_sql = 'select task_id, task_name, plan, plan_date, plan_time from task_schedule ' \
                                   'where is_normal = 1'
        update_task_schedule_sql = 'update task_schedule set is_normal = 0 where task_id = %s'

        task_list_data = self.db.query(select_task_schedule_sql)
        for task_data in task_list_data:
            if '月' == task_data[2]:
                if task_data[3] == arrow.get(self.business_date).format('D'):
                    task_list.append(task_data)
            elif '周' == task_data[2]:
                if int(task_data[3]) == arrow.get(self.business_date).isoweekday():
                    task_list.append(task_data)
            elif '日' == task_data[2]:
                task_list.append(task_data)
            else:
                self.db.exec_one(update_task_schedule_sql, [task_data[0]])
                task_list.append(task_data)

        return task_list

    def create_task(self, task):
        task_id, task_name, plan, plan_date, plan_time = task
        create_time = update_time = arrow.now().format("YYYY-MM-DD HH:mm:ss")
        query_task_record_sql = "select count(1) from task_record where task_id = %s and business_date = '%s';"
        insert_task_record_sql = 'insert into task_record (task_id, task_name, business_date, status, exec_log, ' \
                                 'create_time, update_time) values (%s, %s, %s, %s, %s, %s, %s);'
        update_task_record_sql = "update task_record set status = 1, exec_log = '任务生成', update_time = %s " \
                                 "where task_id = %s;"
        # 需要判断是否创建任务
        if self.db.query_one(query_task_record_sql % (task_id, self.business_date))[0]:
            if plan_time < arrow.now().format('HH:mm'):
                self.db.exec_one(update_task_record_sql, (update_time, task_id))
                self.logger.info('任务-{} 生成'.format(task_name))
                return True
            else:
                return False
        if plan_time > arrow.now().format('HH:mm'):
            self.db.exec_one(insert_task_record_sql,
                             (task_id, task_name, self.business_date, 0, '等待任务生成', create_time, update_time))
            self.logger.info('任务-{} 等待生成'.format(task_name))
            return False
        self.db.exec_one(insert_task_record_sql,
                         (task_id, task_name, self.business_date, 1, '任务生成', create_time, update_time))
        self.logger.info('任务-{} 生成'.format(task_name))
        return True

    def run(self):
        self.logger.info('task_creator 开始生成任务')
        # TODO 生成任务
        # 获取所有的任务列表
        task_list = self.get_task_list()
        existed_task_list = []
        for task in task_list:
            if self.create_task(task):
                existed_task_list.append(task)
        # 生成任务
        while True:
            for task in task_list:
                if task not in existed_task_list and self.create_task(task):
                    existed_task_list.append(task)
            if len(task_list) == len(existed_task_list) or '23:30' < arrow.now().format('HH:mm'):
                break
            time.sleep(60)
        self.logger.info('task_creator 结束生成任务')


if __name__ == '__main__':
    os.chdir(r'D:\programme\python\HXF_Spider')
    TaskCreator().run()
