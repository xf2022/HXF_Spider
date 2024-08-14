"""
各平台的登录基类
不同的平台，只需要改写:
1. 类字典 plat_url —— 用于取各平台内的不同的 url的 cookie,
   其中 key 为名字，会跟着 cookie 存放在数据库中, 如 index 代表平台首页, value 为 url, 仅用于跳转页面获取 cookie
2. __init__ 中的 self.logger, self.plat_type
3. self.browser_operation、 self.verify_process 方法
"""

import os
import socket
import sys
import time
import json
import random
import asyncio
import requests
import traceback
import MySQLdb
import arrow
import re

import cv2
from urllib import request
from pprint import pprint
from datetime import datetime
from config.config import ip_conf, mysql_conf
from auto_login.utils.redis_conf import get_redis_conn
from auto_login.utils.logger import get_stream_logger
from urllib.request import urlretrieve
from pyppeteer import launch
from retrying import retry

sys.path.insert(0, os.getcwd())

mysql_config = {
    'type': 'mysql',
    'host': 'rm-8vbqu0aw00m93f2c5io.mysql.zhangbei.rds.aliyuncs.com',
    'user': 'root',
    'password': 'Userscrm@2020',
    'dbname': 'mh_spider',
    'port': 3306,
    'charset': 'utf8',
}


class AutoLogin:

    def __init__(self, account_id, task_id=None, sub_account_id_info=None):
        self.logger = get_stream_logger('login_base')  # 传入的值会显示在日志输出中，表明是什么程序的日志
        self.redis_conn = get_redis_conn()
        self.shop_cookies = []
        self.shop_info = {}
        self.plats_url = {}
        self.browser = None
        self.page = None
        self.login_status = True  # 记录登录的错误状态
        self.login_error_type = None  # 记录登录的错误类型
        self.login_error_info = None  # 记录登录的错误信息
        self.login_error_id = {}  # 记录登录的错误任务id
        self.download_path = r'C:\code\taobao_auto_login\auto_login\login_img'
        self.account_id = account_id
        self.task_id = task_id
        self.sub_account_id_info = sub_account_id_info

    @retry(stop_max_attempt_number=2, wait_random_min=60)
    async def get_mysql_conn(self):
        """
        获取数据库连接，数据库为 mh_spider
        Returns:
        """
        try:
            db_name = 'mh_spider'
            db = MySQLdb.connect(mysql_config['host'], mysql_config['user'], mysql_config['password'], db_name,
                                 charset='utf8')
            return db
        except Exception as e:
            self.login_status = False
            self.login_error_type = 4
            self.login_error_info = f'获取数据库连接失败，失败原因为: {e}'
            raise

    async def run(self):
        """
        自动化登录程序的开始：
        获取任务 -> 执行任务 -> 判断登录状态 -> 是否存储cookie -> 任务结束继续获取下一个任务
        Returns: 包含店铺id的字典: task['shop_id']
        """
        interval = 10 + random.randint(5, 10)  # 随机间隔

        while True:
            try:
                # 每一个任务的开始，重制任务状态记录
                self.login_status = True
                self.login_error_info = None
                self.login_error_type = None
                self.login_error_id = {}

                # task = await self.get_shop_task()
                # if task:
                #     account_id = task['account_id']
                self.shop_info = await self.get_shop_info(self.account_id)

                # 子账号和主账号的逻辑不同，需要标识
                if self.shop_info['parent_account'] != '0':
                    self.logger.info(f"该账号拥有子账号，需要循环获取cookie")
                    self.shop_info['have_sub_account'] = True
                else:
                    self.logger.info(f"该账号无子账号，直接获取cookie")
                    self.shop_info['have_sub_account'] = False

                if self.shop_info:
                    account_id = self.shop_info['account_id']
                    shop_id = self.shop_info['shop_id']
                    shop_type = self.shop_info['shop_type']
                    self.logger.info(f'当前任务： accountId: {account_id}, shopID: {shop_id}, shopType: {shop_type}')
                    await self.browser_operation()

                self.logger.info('任务完成, 休眠{}s'.format(interval))
                # await self.check_task_status()
                time.sleep(interval)
                # else:
                #     self.logger.info('暂时没有任务, 休眠30m'.format(interval))
                #     time.sleep(60 * 30)
                #     await self.update_task_status_to_wait()  # 将更新任务状态为等待

            except Exception as e:
                self.login_status = False
                self.login_error_type = 4 if not self.login_error_type else self.login_error_type
                self.login_error_info = repr(e)
                self.logger.error(f'任务执行失败({e}) —— ' + self.login_error_info + f' 休眠{interval}s')
                await self.check_task_status(account_id=self.account_id, task_id=self.task_id)
                time.sleep(interval)

            if self.browser:
                await self.browser.close()
            break

    async def get_mc_conn(self):
        """
        获取猫池的数据库连接，数据库为 spcard
        Returns:
        """
        try:
            db_name = 'spcard'
            host = '192.168.3.10'
            user = 'root'
            pass_wd = 'Userscrm__2020'
            db = MySQLdb.connect(host, user, pass_wd, db_name, charset='utf8')
            return db
        except Exception as e:
            self.login_status = False
            self.login_error_type = 4
            self.login_error_info = f'获取猫池数据库连接失败，失败原因为: {e}'
            raise

    async def check_account_plat(self):
        db = await self.get_mysql_conn()
        cursor = db.cursor()

        search_sql = f"SELECT DISTINCT shop_type FROM t_shop_account WHERE account_id = '{self.account_id}'"
        cursor.execute(search_sql)
        self.plat_type = cursor.fetchall()[0][0]

        db.close()

    async def get_shop_info(self, account_id):
        """
        从 mh_manager.shop_account 数据库中获取店铺账号密码等相关信息
        Args:
            account_id: 账号id => shop_account.id
        Returns: 账号id为 account_id 的账号密码等相关信息的字段 self.shop_info
        """
        shop_info = {}
        self.logger.info(f'获取到的账号id为: {account_id}')

        db = await self.get_mysql_conn()  # 创建数据库连接对象
        cursor = db.cursor()  # 通过游标进行操作

        try:
            main_account_sql = f"""
            select parent_account from t_shop_account where account_id = {account_id}
            """
            cursor.execute(main_account_sql)
            main_account = cursor.fetchone()[0]
            real_account_id = account_id if int(main_account) == 0 else main_account

            search_sql = f"""
            SELECT account_id, shop_id, shop_account, shop_password, shop_type, parent_account 
            FROM t_shop_account WHERE account_id = {real_account_id}
            """
            cursor.execute(search_sql)

            data = cursor.fetchone()
            if data:
                shop_info['account_id'] = account_id
                shop_info['shop_id'] = data[1]
                shop_info['shop_account'] = data[2]
                shop_info['shop_password'] = data[3]
                shop_info['shop_type'] = data[4]
                shop_info['parent_account'] = data[5]
            else:
                db.close()
                self.login_status = False
                self.login_error_type = 4
                self.login_error_info = f'获取账号id: {account_id} 的相关信息失败，错误原因为: "获取不到相关账号信息"'
                raise

            db.close()
            return shop_info

        except Exception as e:
            db.close()
            self.login_status = False
            self.login_error_type = 4
            self.login_error_info = f'获取账号id: {account_id} 的相关信息失败，错误原因为: {e}' \
                if not self.login_error_info else self.login_error_info
            raise

    async def get_plat_address(self, shop_type):
        """
        获取平台程序地址
        Returns:

        """
        db = await self.get_mysql_conn()
        cursor = db.cursor()  # 通过游标进行操作
        sql = f"select process_addr from t_process where name ='{shop_type}'"
        cursor.execute(sql)
        plat_address = cursor.fetchone()
        return plat_address[0]

    async def browser_operation(self):
        """
        开始浏览器自动化登录操作
        每个平台改写此方法
        Returns:
        """
        pass

    async def verify_process(self):
        """
        判断是否有滑块并处理
        Returns:
        """
        self.logger.info(f'accountID: {self.shop_info["account_id"]} shopID: {self.shop_info["shop_id"]} 开始处理滑块')

        # 重试次数
        for i in range(10):
            try:
                if i == 0:
                    if not await self.page.J('#captcha-verify-image') and '登录' in await self.page.title():
                        self.login_status = False
                        self.login_error_type = 2 if not self.login_error_type else self.login_error_type
                        self.login_error_info = '自动化程序出错，没有出现滑块，登录失败' if not self.login_error_info else self.login_error_info
                        raise Exception(self.login_error_info)

                # 判断是否出现滑块
                if await self.page.J('#captcha-verify-image'):
                    # 获取图片链接
                    bgd_img_url = await self.page.Jeval('#captcha-verify-image', 'el => el.src')  # 背景图片
                    gap_url = await self.page.Jeval(
                        '#ecomLoginForm-slide-container > div > div.captcha_verify_img--wrapper.sc-gZMcBi.jzVByM > img.captcha_verify_img_slide.react-draggable.sc-VigVT.ggNWOG',
                        'el => el.src')  # 缺口图片

                    # 下载图片
                    urlretrieve(bgd_img_url, os.path.join(self.download_path,
                                                          f"{self.shop_info['account_id']}_{self.plat_type}_bgd.png"))
                    urlretrieve(gap_url, os.path.join(self.download_path,
                                                      f"{self.shop_info['account_id']}_{self.plat_type}_gap.png"))
                    await self.page.waitFor(3000)

                    # 获取滑块边界框
                    el = await self.page.xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
                    border = await el[0].boundingBox()

                    await self.page.hover('#secsdk-captcha-drag-wrapper :nth-child(2)')  # 鼠标悬停滑块按钮
                    drag_distance = await self.get_distance()  # 灰度匹配获取缺口距离

                    await self.drag_captcha(border, drag_distance)  # 拖拽验证滑块
                else:
                    self.logger.info(f'accountID: {self.shop_info["account_id"]} '
                                     f'shopID: {self.shop_info["shop_id"]} 滑块校验成功，等待页面跳转')
                    await self.page.waitFor(3000)  # 等待页面跳转
                    break

            except Exception as e:
                self.login_status = False
                self.login_error_type = 1 if not self.login_error_type else self.login_error_type
                self.login_error_info = f'自动化处理滑块出错，错误原因: {e}' if not self.login_error_info else self.login_error_info

                refresh_element = await self.page.Jx('//span[contains(text(), "刷新")]')
                await refresh_element[0].click()
                await self.page.waitFor(1000)
        else:
            raise Exception(self.login_error_info)

    async def check_login_status(self):
        """
        校验登录状态
        Returns:
        """
        self.page.waitFor(3000)
        print('网页标题:', await self.page.title())
        if '登录' in await self.page.title():
            self.login_status = False
            self.login_error_type = 2

            if await self.page.Jx('//div[contains(text(), "风险")]'):
                self.login_error_info = f'accountID: {self.shop_info["account_id"]} 账号存在风险，登陆失败'
            else:
                self.login_error_info = '登录没有成功跳转页面，登录失败'
            raise Exception(self.login_error_info)
        elif '验证' in await self.page.title() or '认证' in await self.page.title():
            self.login_status = False
            self.login_error_type = 3
            self.login_error_info = f'accountID: {self.shop_info["account_id"]} 需要验证码，登陆失败'
            raise Exception(self.login_error_info)

        self.logger.info(f'accountID: {self.shop_info["account_id"]} '
                         f'shopID: {self.shop_info["shop_id"]} 跳转页面成功，准备获取cookie')
        return True

    async def get_distance(self):
        """
        使用 cv2 库 灰度匹配获取缺口距离
        Returns:
        """
        bgd_img = cv2.imread(
            os.path.join(self.download_path, f'{self.shop_info["account_id"]}_{self.plat_type}_bgd.png'), 0)
        gap_img = cv2.imread(
            os.path.join(self.download_path, f'{self.shop_info["account_id"]}_{self.plat_type}_gap.png'), 0)
        res = cv2.matchTemplate(bgd_img, gap_img, cv2.TM_CCORR_NORMED)

        x_min_value = cv2.minMaxLoc(res)[2][0]  # x 坐标的最小值
        drag_distance = x_min_value * 340 / 552  # 拖拽距离

        return drag_distance

    async def drag_captcha(self, border, drag_distance):
        """
        拖拽滑块
        Args:
            border: 当前滑块距离
            drag_distance: 需要移动的距离
        Returns:
        """
        try:
            await self.page.mouse.down()
            await self.page.mouse.move(border['x'] + drag_distance + random.uniform(30, 33), border['y'], {'steps': 30})
            await self.page.waitFor(random.randint(300, 700))
            await self.page.mouse.move(border['x'] + drag_distance + 16, border['y'], {'steps': 30})
            await self.page.mouse.up()
            await self.page.waitFor(3000)
        except Exception as e:
            self.login_status = False
            self.login_error_info = f'处理滑块出错，错误原因为: {e}'
            raise

    async def get_all_sub_account_info(self):
        """
        查询该账号下所有的子账号信息 : {shop_id: shop_name}
        Returns:
        """
        parent_account = self.shop_info['parent_account']

        db = await self.get_mysql_conn()
        cursor = db.cursor()  # 通过游标进行操作

        # 查询该账号是否拥有子账号
        search_sql = f"SELECT account_id, shop_id, shop_name, shop_account FROM t_shop_account " \
                     f"WHERE parent_account = '{parent_account}' AND account_id != parent_account"
        cursor.execute(search_sql)
        db.close()

        data = cursor.fetchall()
        all_sub_account_info = {}
        if data:
            for result in data:
                all_sub_account_info[result[0]] = [result[1], result[2], result[3]]
            return all_sub_account_info

        return False

    async def goto_correct_shop(self, shop_name):
        """
        根据传进来的店铺名，匹配网页中的店铺名，进行跳转
        Args:
            shop_name: 数据库中的店铺名 shop_account.shop_name
        Returns:
        """
        elem = await self.page.xpath('//button[@class="ant-btn ant-btn-primary"]/span[text()="同 意"]')
        if elem:
            await elem[0].click()
            await self.page.waitFor(3000)
        shop_name_element = await self.page.xpath(f'//div[contains(text(), "{shop_name}")]')
        if not shop_name_element:
            shop_name_element = await self.page.xpath(f'//span[contains(text(), "{shop_name}")]')
        if shop_name_element:
            button_element = await shop_name_element[0].xpath(f"../following-sibling::div[contains(text(), '进入店铺')]")
            if button_element:
                await button_element[0].click()
            else:
                if await self.page.xpath(f'//div[text()="{shop_name}"]'):
                    self.logger.info(f'当前页面为 {shop_name} 店铺, 无需点击登录')
                else:
                    raise Exception(f'店铺名：{shop_name}，在登录列表页找不到该店铺')
        else:
            raise Exception(f'店铺名：{shop_name}，在登录列表页找不到该店铺')

    async def get_cookies(self, account_id):
        """
        获取各平台cookie，目前只需要首页cookie
        Returns:
        """
        await self.get_plats_url(account_id)
        plats_cookies = {}
        error_info = ''
        for plat in self.plats_url:
            for i in range(3):
                try:
                    self.logger.info(f'accountID: {account_id} 正在获取平台: {plat} 的 cookie')

                    # 跳转页面
                    if self.plats_url[plat] != self.page.url:
                        await self.page.goto(self.plats_url[plat], {'timeout': 30000, })
                        await self.page.waitFor(1000)
                        await asyncio.sleep(10)

                    # 获取浏览器cookie
                    cookies = await self.page.cookies()
                    cookies_str = '';
                    i = 0
                    for item in cookies:
                        i += 1
                        cookies_str += item['name'] + '=' + item['value']
                        if i != len(cookies):
                            cookies_str += ';'

                    # 添加该平台cookie
                    plats_cookies[plat] = cookies_str
                    self.logger.info(f'accountID: {account_id} 平台: {plat} 的 cookie 获取成功')
                    break
                except Exception as error_info:
                    self.logger.error(f'accountID: {account_id}，'
                                      f'平台: {plat} 获取cookie失败，错误原因为: {error_info}')
            else:
                self.login_status = False
                self.login_error_type = 4
                # 多个平台出错时需要组装
                self.login_error_info = f'accountId: {account_id} 平台: {plat} 获取cookie失败' \
                    if not self.login_error_info else f' {self.login_error_info}; accountId: {account_id} 平台: {plat} 获取cookie失败'
                self.login_error_id[f'{account_id}_{plat}'] = repr(error_info)

        self.plats_url.clear()

        return plats_cookies

    async def get_plats_url(self, account_id):
        """
        从数据库中查询每个账号对应的所有平台的类型和url
        Returns:
        """
        if not self.sub_account_id_info:
            db = await self.get_mysql_conn()
            cursor = db.cursor()

            search_sql = f"SELECT page_type, url FROM t_account_have_plat " \
                         f"WHERE account_id = '{account_id}' AND plat_type = '{self.plat_type}'"
            cursor.execute(search_sql)
            plats_url = cursor.fetchall()
            db.close()

            for plat_url in plats_url:
                self.plats_url[plat_url[0]] = plat_url[1]

        else:

            self.plats_url = {value['page_type']: value['url'] for value in self.sub_account_id_info.values()
                              if value['sub_account_id'] == account_id}

    async def push_cookies(self, account_id, shop_id, plats_cookies):
        """
        循环 plats_cookies 存储cookie到数据库
        Args:
            account_id: shop_account.id
            shop_id: shop_account.shop_id
            plats_cookies:
        Returns:

        """
        db = await self.get_mysql_conn()
        cursor = db.cursor()

        for plat in plats_cookies:
            for db_name in ['t_shop_cookies', 'mh_manager.shop_cookies']:
                sql = f"""
                    INSERT INTO {db_name}
                    (account_id, shop_id, shop_type, cookies, page_type, update_time)
                    VALUES('{account_id}', '{shop_id}', '{self.plat_type}', '{plats_cookies[plat]}',
                            '{plat}', now())
                    ON DUPLICATE KEY UPDATE 
                    account_id = '{account_id}',
                    shop_type = '{self.plat_type}',
                    page_type = '{plat}',
                    cookies = '{plats_cookies[plat]}',
                    update_time=now()

                """
                cursor.execute(sql)
                self.logger.info(F'accountID: {account_id}, shopID: {shop_id} 平台: {plat} cookie 存储成功')
                db.commit()
            # 将获取cookies成功的店铺更改状态
            await self.check_task_status(account_id, plat)
        db.close()

    async def get_chrome_info(self, account_id):
        db = await self.get_mysql_conn()  # 创建数据库连接对象
        cursor = db.cursor()  # 通过游标进行操作
        search_sql = f"SELECT chrome_command from t_store WHERE id = {account_id}"
        cursor.execute(search_sql)
        result = cursor.fetchone()
        if result:
            return result[0].replace('chrome.exe ', '')
        self.logger.error(f'账号id:{account_id}, 在t_store表无chrome指令')

    async def check_task_status(self, account_id=None, plat=None, task_id=None):
        """
        校验任务状态，发送监控
        Returns:
        """
        try:
            db = await self.get_mysql_conn()
            cursor = db.cursor()

            # 如果在休眠中没有任务，则不发监控
            if not self.shop_info:
                return

            # 根据登录状态更新任务状态
            if self.login_status:
                update_sql = f"""
                UPDATE t_cookies_task
                SET status = 2, res_msg = '登录成功', update_time = now()
                WHERE sub_account_id = '{account_id}' and page_type = '{plat}'
                """
                cursor.execute(update_sql)
                db.commit()
            else:
                if self.login_error_id:
                    for key, value in self.login_error_id.items():
                        update_sql = f"""
                            UPDATE t_cookies_task
                            SET status = 3, 
                            res_msg = "{value}", update_time = now()
                            WHERE sub_account_id = '{key.split('_')[0]}' and page_type = '{key.split('_')[1]}'
                        """
                        cursor.execute(update_sql)
                        db.commit()
                else:
                    if task_id:
                        update_sql = f"""
                                    UPDATE t_cookies_task
                                    SET status = 3, 
                                    res_msg = "{self.login_error_info.replace(r'"', r'')}", update_time = now()
                                    WHERE id in ({task_id})
                                    """
                    else:
                        update_sql = f"""
                        UPDATE t_cookies_task
                        SET status = 3, 
                        res_msg = "{self.login_error_info.replace(r'"', r'')}", update_time = now()
                        WHERE sub_account_id = '{account_id}' {f'and page_type = "{plat}"' if plat else ''}
                        """
                    cursor.execute(update_sql)
                    db.commit()
            db.close()
        except Exception as e:
            self.logger.error(f'更改数据库状态出错，错误原因为: {e}')

    async def update_task_status_to_wait(self):
        """
        更新任务状态为等待
        Returns:bayeryy@aihe123
        """
        self.logger.info('更新任务状态为等待')
        db = await self.get_mysql_conn()
        cursor = db.cursor()

        update_sql = f"UPDATE t_cookies_task SET status = 1 WHERE shop_type = '{self.plat_type}'"
        cursor.execute(update_sql)

        db.commit()
        db.close()



