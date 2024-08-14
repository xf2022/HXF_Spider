import arrow
import pymysql
from setting import MYSQL_CONFIG as CONFIG


def get_db():
    pymysql.connect()


class MySqlSingleConnect:
    def __init__(self):
        self.conn = MySqlSingleConnect._get_conn()
        self.cursor = self.conn.cursor()
        self.conn.autocommit(True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def _get_conn():
        return pymysql.connect(host=CONFIG['host'],
                               port=CONFIG['port'],
                               user=CONFIG['user'],
                               password=CONFIG['password'],
                               database=CONFIG['database'],
                               charset=CONFIG['charset'])

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def query_one(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def delete(self, sql):
        return self.cursor.execute(sql)

    def insert(self, sql, data_tuple):
        self.cursor.execute(sql, data_tuple)
        self.commit()
        data = self.query('select last_insert_id() as id')
        return data[0][0]

    def insert_many(self, sql, data_list):
        return self.cursor.executemany(sql, data_list)

    def exec_many(self, sql, data_list):
        return self.cursor.executemany(sql, data_list)

    def exec_one(self, sql, data_tuple):
        return self.cursor.execute(sql, data_tuple)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        if self.cursor:
            self.cursor.close()
        self.conn.close()

    def begin(self):
        self.conn.begin()

    def end(self, is_normal=True):
        if is_normal:
            self.commit()
        else:
            self.rollback()
        pass


if __name__ == '__main__':
    test = MySqlSingleConnect()
    current_time = arrow.now()
    sql = 'insert into target_website (name, url, description, config, create_time, update_time) values ' \
          '(%s,%s,%s,%s,%s,%s)'
    # print(test.delete("delete from target_website where name = '极简壁纸'"))
    # test.commit()
    # test.rollback()
    test.begin()
    test.exec_one(sql, ('极简壁纸', 'https://bz.zzzmh.cn/', '', '', current_time, current_time))
    test.end()
    # print(test.insert(sql, ('极简壁纸', 'https://bz.zzzmh.cn/', '', '', current_time, current_time)))
    # test._get_conn()
