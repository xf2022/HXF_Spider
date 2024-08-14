#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : Huangzt
# Date: 2021/11/23

"""
京东商智登录
"""

import os
import sys
import asyncio

import cv2
import pyppeteer
import random
from urllib.request import urlretrieve
from pyppeteer import launch

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

class JDLogin():

    def __init__(self, account_id, account_pwd, task_id=None, sub_account_id_info=None):
        self.account_id = account_id
        self.account_pwd = account_pwd
        self.download_path = "D:/Image/jd_login/"
        # self.logger = get_stream_logger('jd_login')

    async def browser_operation(self):
        """
        开始浏览器自动化登录操作
        Returns:
        """
        shop_account = self.account_id
        shop_password = self.account_pwd

        self.login_status = True
        self.login_error_info = None
        self.login_error_type = None
        # 浏览器下载文件地址
        chrome_info = ''
        # 登录重试3次
        for i in range(3):
            try:
                # 浏览器参数配置
                browser_config = {
                    'headless': False,  # 是否无头模式运行
                    'dumpio': True,  # 防止多开导致的假死
                    'ignoreHTTPSErrors': True,
                    'executablePath': r'C:\Users\HXF\AppData\Local\Google\Chrome\Application\chrome.exe',
                    'args': ['--no--sandbox',  # 取消沙盒模式，放开权限
                             '--disable-infobars',  # 不显示信息栏
                             '--window-size=1366,768',
                             '--disable-blink-features=AutomationControlled'
                             ]  # 文件保存目录
                }
                # 创建浏览器实例
                self.browser = await pyppeteer.launch(browser_config)
                # 创建页面对象
                self.page = await self.browser.newPage()
                await self.page.setViewport({'width': 1366, 'height': 768})

                # 移除 Pyppeteer 中的window.navigator.webdriver，以不被识别出是脚本
                await self.page.evaluateOnNewDocument(
                    '''
                    () => {
                    Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                    })
                    }
                    '''
                )

                # 开始登录操作
                await self.page.goto('https://passport.jd.com/new/login.aspx?ReturnUrl=https://vc.jd.com',
                                     {'timeout': 30000})

                # 点击密码登录
                # if await self.page.J('.form-login-type-toggle#pwd-login'):
                #     await self.page.click('.form-login-type-toggle#pwd-login')
                #     await self.page.waitFor(1000)
                # else:
                #     ele = await self.page.Jx('//div[text()="换个账号登录"]')
                #     if ele:
                #         await ele[0].click()
                #         await self.page.waitFor(1000)
                #     if await self.page.J('.form-login-type-toggle#pwd-login'):
                #         await self.page.click('.form-login-type-toggle#pwd-login')
                #         await self.page.waitFor(1000)

                # 输入账号密码
                await self.page.click('#loginname.itxt')
                await self.page.evaluate('document.querySelector("#loginname.itxt").value=""')
                await self.page.type('#loginname.itxt', shop_account, {'delay': random.randint(60, 121)})  # 账号

                await self.page.click('#nloginpwd.itxt.itxt-error')
                await self.page.type('#nloginpwd.itxt.itxt-error', shop_password,
                                     {'delay': random.randint(100, 151)})  # 密码

                if 'login' in self.page.url:
                    await self.page.click('.login-btn')
                    await self.page.waitFor(5000)

                    # 校验滑块验证码
                    await self.verify_process()
                    # 校验登录状态
                    await self.check_login_status()

                # 如果该账号拥有子账号，则循环子账号取cookie
                # if self.shop_info['have_sub_account']:
                #
                #     # 找出所有的子账号信息 {shop_id: shop_name}
                #     all_sub_account_info = await self.get_all_sub_account_info()
                #     self.logger.info(f'accountID: {self.shop_info["account_id"]} 拥有子账号或为子账号，准备用主账号获取各账号cookie')
                #
                #     # 执行循环绑定的多店铺操作
                #     for account_id in all_sub_account_info:
                #         # 投放账号  代理账号
                #         account_url = ['https://jzt.jd.com/account/#/accountmanage',
                #                        'https://jzt.jd.com/account/#/agencyAccount']
                #         for _url in account_url:
                #             await self.page.goto(_url)
                #             await self.page.waitFor(3000)
                #
                #             shop_id = all_sub_account_info[account_id][0]
                #             shop_name = all_sub_account_info[account_id][1]
                #             shop_item_account = all_sub_account_info[account_id][2]
                #             continue_flag = await self.jzt_goto_correct_shop(shop_id, account_id,
                #                                                              shop_item_account)  # 京准通需要根据子账号名，进行点击跳转
                #
                #             if not continue_flag:
                #                 self.logger.info(f'accountID: {account_id} 子账号: {shop_item_account} 的 cookie 获取成功')
                #                 break

                # 如果没有，则直接登录获取各平台cookie
                # else:

                # self.logger.info(f'accountID: {self.shop_info["account_id"]} 没有子账号，准备获取各平台cookie')
                # await self.page.goto('https://jzt.jd.com')
                # 获取 cookie 并将cookie存入数据库
                # plats_cookies = await self.get_cookies(self.shop_info['account_id'])
                # await self.push_cookies(self.shop_info['account_id'], self.shop_info['shop_id'], plats_cookies)

                break
            except Exception as e:
                await self.browser.close()  # 关闭浏览器
                self.login_status = True  # 重试时重置登录状态
                self.login_error_type = 4 if not self.login_error_type else self.login_error_type
                self.login_error_info = f'任务过程出错，错误原因为: {e}' if not self.login_error_info else self.login_error_info
                # self.logger.error(self.login_error_info + ('，即将重试' if i != range(3)[-1] else '，结束重试'))
        else:
            self.login_status = False  # 重试次数用完后，标记登录状态为失败
            raise

    # async def get_all_sub_account_info(self):
    #     """
    #     查询该账号下所有的子账号信息 : {shop_id: shop_name}
    #     京准通需要或许主账号cookies
    #     Returns:
    #     """
    #     parent_account = self.shop_info['parent_account']
    #
    #     db = await self.get_mysql_conn()
    #     cursor = db.cursor()
    #
    #     # 查询该账号是否拥有子账号
    #     search_sql = f"SELECT account_id, shop_id, shop_name, shop_account FROM t_shop_account " \
    #                  f"WHERE parent_account = '{parent_account}' AND shop_id is not NULL"
    #     cursor.execute(search_sql)
    #     db.close()
    #
    #     data = cursor.fetchall()
    #     all_sub_account_info = {}
    #     if data:
    #         for result in data:
    #             all_sub_account_info[result[0]] = [result[1], result[2], result[3]]
    #         return all_sub_account_info
    #
    #     return False

    # async def jzt_goto_correct_shop(self, shop_id, account_id, account_name):
    #     """
    #     根据传进来的店铺名，匹配网页中的店铺名，进行跳转
    #     Args:
    #         shop_name: 数据库中的店铺名 shop_account.shop_name
    #     Returns:
    #     """
    #     # 选择100条
    #     select_page_button = await self.page.Jx("//button[@class='jad-btn jad-btn-default']")
    #     await select_page_button[0].click()
    #     await self.page.waitFor(3000)
    #     select_page = await self.page.Jx(
    #         "//div[@class='jad-popover-poper jad-pagination-popper-pageSize']//ul/li[last()]")
    #     await select_page[0].click()
    #     await self.page.waitFor(3000)
    #     # 查找所有子账号
    #     account_elements = await self.page.Jx('//div[@class="jad-table-content"]//tbody/tr')
    #     for account_tr in account_elements:  # 循环页面上的子账号列表
    #         try:
    #             if 'accountmanage' in self.page.target.url:
    #                 pin_ele = await account_tr.xpath('./td[1]/div/div')
    #                 available_ele = await account_tr.xpath('./td[4]/div')
    #                 pin_name = await (await pin_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上PIN
    #                 is_available = await (await available_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上账号状态
    #                 # if is_available.strip() != '正常':
    #                 #     continue
    #                 if account_name == pin_name:
    #                     click_ele = await account_tr.xpath('.//a[text()="查看登录账号"]')
    #                     await click_ele[0].click()
    #                     await self.page.waitFor(5000)
    #                     pages_list = await self.browser.pages()
    #                     self.page = pages_list[-1]
    #                     await self.page.setViewport({"width": 1366, "height": 768})
    #                     await self.page.waitFor(3000)
    #
    #                     # 获取 cookie 并将cookie存入数据库
    #                     plats_cookies = await self.get_cookies(account_id)
    #                     await self.push_cookies(account_id, shop_id, plats_cookies)
    #                     await self.page.waitFor(3000)
    #                     await pages_list[-1].close()
    #                     await self.page.waitFor(1000)
    #                     self.page = pages_list[-2]
    #                     return False
    #                 continue
    #
    #             elif 'agencyAccount' in self.page.target.url:
    #                 pin_ele = await account_tr.xpath('./td[2]/div/div')
    #                 pin_name = await (await pin_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上PIN
    #
    #                 if account_name == pin_name:
    #                     click_ele = await account_tr.xpath('.//a[contains(text(), "登录查看账号")]')
    #
    #                     await click_ele[0].click()
    #                     await self.page.waitFor(5000)
    #                     pages_list = await self.browser.pages()
    #                     self.page = pages_list[-1]
    #                     await self.page.setViewport({"width": 1366, "height": 768})
    #                     await self.page.waitFor(3000)
    #
    #                     # 获取 cookie 并将cookie存入数据库
    #                     plats_cookies = await self.get_cookies(account_id)
    #                     await self.push_cookies(account_id, shop_id, plats_cookies)
    #                     await self.page.waitFor(3000)
    #                     await pages_list[-1].close()
    #                     await self.page.waitFor(1000)
    #                     self.page = pages_list[-2]
    #                     return False
    #                 continue
    #
    #         except Exception as e:
    #             import traceback
    #             traceback.print_exc()
    #     return True

    async def verify_process(self):
        """
        判断是否有滑块并处理
        Returns:
        """
        # self.logger.info(f'accountID: {self.shop_info["account_id"]} shopID: {self.shop_info["shop_id"]} 开始处理滑块')

        # 重试次数
        for i in range(10):
            try:
                if i == 0:
                    if not await self.page.J('.JDJRV-slide ') and '登录' in await self.page.title():
                        self.login_status = False
                        self.login_error_type = 2 if not self.login_error_type else self.login_error_type

                        if await self.page.Jx('//div[contains(text(), "风险")]'):
                            self.login_error_info = f'accountID: {self.account_id} 账号存在风险，登陆失败'
                        else:
                            self.login_error_info = '自动化程序出错，没有出现滑块，登录失败' if not self.login_error_info else self.login_error_info
                        raise Exception(self.login_error_info)

                # 判断是否出现滑块
                if await self.page.J('.JDJRV-slide ') and not await self.page.Jx('//div[contains(text(), "风险")]'):
                    # 获取图片链接
                    bgd_img_url = await self.page.Jeval('.JDJRV-bigimg > img', 'el => el.src')  # 背景图片
                    gap_url = await self.page.Jeval('.JDJRV-smallimg > img', 'el => el.src')  # 缺口图片

                    # 下载图片
                    urlretrieve(bgd_img_url, os.path.join(self.download_path,
                                                          f"01_jd_bgd.png"))
                    urlretrieve(gap_url, os.path.join(self.download_path,
                                                      f"01_jd_gap.png"))
                    await self.page.waitFor(3000)

                    # 获取滑块边界框
                    el = await self.page.xpath('//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')
                    border = await el[0].boundingBox()

                    await self.page.hover('.JDJRV-slide-inner.JDJRV-slide-btn')  # 鼠标悬停滑块按钮
                    drag_distance = await self.get_distance()  # 灰度匹配获取缺口距离

                    await self.drag_captcha(border, drag_distance + 20)  # 拖拽验证滑块
                else:
                    # self.logger.info(f'accountID: {self.shop_info["account_id"]} '
                    #                  f'shopID: {self.shop_info["shop_id"]} 滑块校验成功，等待页面跳转')
                    await self.page.waitFor(3000)  # 等待页面跳转
                    break

            except Exception as e:
                self.login_status = False
                self.login_error_type = 1 if not self.login_error_type else self.login_error_type
                self.login_error_info = f'自动化处理滑块出错，错误原因: {e}' if not self.login_error_info else self.login_error_info

                refresh_element = await self.page.Jx('//span[contains(text(), "换一张")]')
                await refresh_element[0].click()
                await self.page.waitFor(1000)
        else:
            raise Exception(self.login_error_info)

    async def get_distance(self):
        """
        使用 cv2 库 灰度匹配获取缺口距离
        Returns:
        """
        bgd_img = cv2.imread(
            os.path.join(self.download_path, f'01_jd_bgd.png'), 0)
        gap_img = cv2.imread(
            os.path.join(self.download_path, f'01_jd_gap.png'), 0)
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

    async def check_login_status(self):
        """
        校验登录状态
        Returns:
        """
        await self.page.waitFor(3000)
        print('网页标题:', await self.page.title())
        if '登录' in await self.page.title():
            self.login_status = False
            self.login_error_type = 2

            if await self.page.Jx('//div[contains(text(), "风险")]'):
                self.login_error_info = f'accountID: {self.account_id} 账号存在风险，登陆失败'
            else:
                self.login_error_info = '登录没有成功跳转页面，登录失败'
            raise Exception(self.login_error_info)
        elif '验证' in await self.page.title() or '认证' in await self.page.title():
            self.login_status = False
            self.login_error_type = 3
            self.login_error_info = f'accountID: {self.account_id} 需要验证码，登陆失败'
            raise Exception(self.login_error_info)

        # self.logger.info(f'accountID: {self.shop_info["account_id"]} '
        #                  f'shopID: {self.shop_info["shop_id"]} 跳转页面成功，准备获取cookie')
        return True

# class JZTLogin(AutoLogin):
#
#     def __init__(self, account_id, task_id=None, sub_account_id_info=None):
#         super().__init__(account_id, task_id, sub_account_id_info)
#         self.logger = get_stream_logger('jzt_login')
#         # self.plat_type = 'jzt'
#
#     async def browser_operation(self):
#         """
#         开始浏览器自动化登录操作
#         Returns:
#         """
#         shop_account = self.shop_info['shop_account']
#         shop_password = self.shop_info['shop_password']
#         chrome_info = await self.get_chrome_info(self.shop_info['account_id'])
#         # 登录重试3次
#         for i in range(3):
#             try:
#                 # 浏览器参数配置
#                 browser_config = {
#                     'headless': False,  # 是否无头模式运行
#                     'dumpio': True,  # 防止多开导致的假死
#                     'ignoreHTTPSErrors': True,
#                     # 'executablePath': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
#                     'args': ['--no--sandbox',  # 取消沙盒模式，放开权限
#                              '--disable-infobars',  # 不显示信息栏
#                              '--window-size=1366,768',
#                              '--disable-blink-features=AutomationControlled',
#                              chrome_info]  # 文件保存目录
#                 }
#                 # 创建浏览器实例
#                 self.browser = await pyppeteer.launch(browser_config)
#                 # 创建页面对象
#                 self.page = await self.browser.newPage()
#                 await self.page.setViewport({'width': 1366, 'height': 500})
#
#                 # 移除 Pyppeteer 中的window.navigator.webdriver，以不被识别出是脚本
#                 await self.page.evaluateOnNewDocument(
#                     '''
#                     () => {
#                     Object.defineProperty(navigator, 'webdriver', {
#                     get: () => undefined
#                     })
#                     }
#                     '''
#                 )
#
#                 # 开始登录操作
#                 await self.page.goto('https://passport.jd.com/new/login.aspx?ReturnUrl=https://vc.jd.com',
#                                      {'timeout': 30000})
#
#                 # 点击密码登录
#                 if await self.page.J('.form-login-type-toggle#pwd-login'):
#                     await self.page.click('.form-login-type-toggle#pwd-login')
#                     await self.page.waitFor(1000)
#
#                 # 输入账号密码
#                 await self.page.click('#loginname.itxt')
#                 await self.page.evaluate('document.querySelector("#loginname.itxt").value=""')
#                 await self.page.type('#loginname.itxt', shop_account, {'delay': random.randint(60, 121)})  # 账号
#
#                 await self.page.click('#nloginpwd.itxt.itxt-error')
#                 await self.page.type('#nloginpwd.itxt.itxt-error', shop_password,
#                                      {'delay': random.randint(100, 151)})  # 密码
#
#                 if 'login' in self.page.url:
#                     await self.page.click('.login-btn')
#                     await self.page.waitFor(3000)
#
#                     # 校验滑块验证码
#                     await self.verify_process()
#                     # 校验登录状态
#                     await self.check_login_status()
#
#                 # 如果该账号拥有子账号，则循环子账号取cookie
#                 if self.shop_info['have_sub_account']:
#                     # 找出所有的子账号信息 {shop_id: shop_name}
#                     if not self.sub_account_id_info:
#                         all_sub_account_info = await self.get_all_sub_account_info()
#                     else:
#                         all_sub_account_info = {value['sub_account_id']: [value['shop_id'],
#                                                                           value['shop_name'], value['login_name']]
#                                                 for key, value in self.sub_account_id_info.items()}
#
#                     self.logger.info(f'accountID: {self.shop_info["account_id"]} 拥有子账号或为子账号，准备用主账号获取各账号cookie')
#                     # 执行循环绑定的多店铺操作
#                     for account_id in all_sub_account_info:
#                         # 投放账号  代理账号
#                         account_url = ['https://jzt.jd.com/account/#/accountmanage',
#                                        'https://jzt.jd.com/account/#/agencyAccount']
#                         for _url in account_url:
#                             await self.page.goto(_url)
#                             await self.page.waitFor(3000)
#
#                             shop_id = all_sub_account_info[account_id][0]
#                             shop_name = all_sub_account_info[account_id][1]
#                             shop_item_account = all_sub_account_info[account_id][2]
#                             continue_flag = await self.jzt_goto_correct_shop(shop_id, account_id,
#                                                                              shop_item_account)  # 京准通需要根据子账号名，进行点击跳转
#
#                             if not continue_flag:
#                                 self.logger.info(f'accountID: {account_id} 子账号: {shop_item_account} 的 cookie 获取成功')
#                                 break
#
#                 # 如果没有，则直接登录获取各平台cookie
#                 else:
#                     self.logger.info(f'accountID: {self.shop_info["account_id"]} 没有子账号，准备获取各平台cookie')
#                     # await self.page.goto('https://jzt.jd.com')
#                     # 获取 cookie 并将cookie存入数据库
#                     plats_cookies = await self.get_cookies(self.shop_info['account_id'])
#                     await self.push_cookies(self.shop_info['account_id'], self.shop_info['shop_id'], plats_cookies)
#
#                 break
#             except Exception as e:
#                 await self.browser.close()  # 关闭浏览器
#                 self.login_status = True  # 重试时重置登录状态
#                 self.login_error_type = 4 if not self.login_error_type else self.login_error_type
#                 self.login_error_info = f'任务过程出错，错误原因为: {e}' if not self.login_error_info else self.login_error_info
#                 self.logger.error(self.login_error_info + ('，即将重试' if i != range(3)[-1] else '，结束重试'))
#         else:
#             self.login_status = False  # 重试次数用完后，标记登录状态为失败
#             raise
#
#     async def get_all_sub_account_info(self):
#         """
#         查询该账号下所有的子账号信息 : {shop_id: shop_name}
#         京准通需要或许主账号cookies
#         Returns:
#         """
#         parent_account = self.shop_info['parent_account']
#
#         if self.sub_account_id_info is not None:
#             total_sub_id = ['%s' % _val['sub_account_id'] for _val in self.sub_account_id_info.values()]
#         elif self.sub_account_id_info is None and parent_account == self.shop_info['account_id']:
#             total_sub_id = [parent_account]
#         else:
#             total_sub_id = [str(self.shop_info['account_id'])]
#
#         # 查询该账号是否拥有子账号
#         search_sql = f"""
#         SELECT t1.account_id, t1.shop_id, t1.shop_name, t1.shop_account FROM t_shop_account t1
#         left join t_store t2
#         on t1.account_id = t2.id
#         WHERE t1.parent_account = {parent_account} and  t2.status =1
#
#         """
#         db = await self.get_mysql_conn()
#         cursor = db.cursor()
#
#         cursor.execute(search_sql)
#         db.close()
#
#         data = cursor.fetchall()
#         all_sub_account_info = {}
#         if data:
#             for result in data:
#                 if [parent_account] == total_sub_id:
#                     all_sub_account_info[result[0]] = [result[1], result[2], result[3]]
#                 elif result[0] in total_sub_id:
#                     all_sub_account_info[result[0]] = [result[1], result[2], result[3]]
#             return all_sub_account_info
#
#         return False
#
#     async def check_correct_shop(self, item_name):
#         """
#         检查进入的子账号是否为需要的子账号
#         Args:
#             item_name: 数据库中的店铺名 shop_account.shop_name
#         Returns:
#         """
#         elem = await self.page.xpath('//li[@class="jzt-top-menu-item jzt-user"]/span[@class="jzt-user-pin"]')
#
#         page_name = await (await elem[0].getProperty('textContent')).jsonValue()
#
#         if item_name != page_name:
#             raise Exception(f'店铺名：{item_name}，子账号跳转失败')
#
#     async def jzt_goto_correct_shop(self, shop_id, account_id, account_name):
#         """
#         根据传进来的店铺名，匹配网页中的店铺名，进行跳转
#         Args:
#             shop_name: 数据库中的店铺名 shop_account.shop_name
#         Returns:
#         """
#         # 选择100条
#         # select_page_button = await self.page.Jx("//button[@class='jad-btn jad-btn-default jad-btn-medium']")
#         select_page_button2 = await self.page.Jx("//div[@class='jad-pagination-sizer']//button")
#         await select_page_button2[0].click()
#         await self.page.waitFor(3000)
#         try:
#             select_page = await self.page.Jx(
#                 "//div[@class='jad-popover-poper jad-pagination-popper-pageSize']//ul/li[last()]")
#             await select_page[0].click()
#         except:
#             print('无筛选定位')
#         await self.page.waitFor(3000)
#         main_account_elem = await self.page.Jx('//span[@class="jzt-user-pin"]')
#         main_account_name = await (await main_account_elem[0].getProperty('textContent')).jsonValue()  # 获取页面上PIN
#         # 查找所有子账号
#         account_elements = await self.page.Jx('//div[@class="jad-table-content"]//tbody/tr')
#         for _index, account_tr in enumerate(account_elements):  # 循环页面上的子账号列表
#             try:
#                 if 'accountmanage' in self.page.target.url:
#                     pin_ele = await account_tr.xpath('./td[2]/div/div')
#                     # available_ele = await account_tr.xpath('./td[4]/div')
#                     pin_name = await (await pin_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上PIN
#                     # is_available = await (await available_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上账号状态
#                     # if is_available.strip() != '正常':
#                     #     continue
#                     if account_name == main_account_name:
#                         # 主账号无【查看登录账号】
#                         await self.page.setViewport({"width": 1366, "height": 768})
#                         await self.page.waitFor(3000)
#                         await self.check_correct_shop(account_name)
#                         # 获取 cookie 并将cookie存入数据库
#                         plats_cookies = await self.get_cookies(account_id)
#                         await self.push_cookies(account_id, shop_id, plats_cookies)
#                         await self.page.waitFor(3000)
#                     elif account_name == pin_name:
#                         click_ele = await account_tr.xpath('.//a[contains(text(), "查看登录账号")]')
#                         await self.page.evaluate('el => el.click()', click_ele[0])
#                         await self.page.waitFor(5000)
#                         pages_list = await self.browser.pages()
#                         if len(pages_list) < 3 or 'account/#/accountmanage' in pages_list[-1].url:
#                             raise Exception(f'子账号：{account_name}，点击进入子账号页面失败')
#                         self.page = pages_list[-1]
#                         await self.page.setViewport({"width": 1366, "height": 768})
#                         await self.page.waitFor(3000)
#                         await self.check_correct_shop(account_name)
#                         # 获取 cookie 并将cookie存入数据库
#                         plats_cookies = await self.get_cookies(account_id)
#                         await self.push_cookies(account_id, shop_id, plats_cookies)
#                         await self.page.waitFor(3000)
#                         await pages_list[-1].close()
#                         await self.page.waitFor(1000)
#                         self.page = pages_list[-2]
#                         return False
#                     else:
#                         if _index == len(account_elements) - 1:
#                             raise Exception(f"{account_name} url地址:accountmanage,未找到对应的子账号")
#                         else:
#                             continue
#
#                 elif 'agencyAccount' in self.page.target.url:
#                     # pin_ele = await account_tr.xpath('./td[1]/div')
#                     pin_ele = await account_tr.xpath('./td[2]/div/div')
#                     pin_name = await (await pin_ele[0].getProperty('textContent')).jsonValue()  # 获取页面上PIN
#
#                     if account_name == pin_name:
#                         click_ele = await account_tr.xpath('.//a[contains(text(), "登录查看账号")]')
#
#                         await click_ele[0].click()
#                         await self.page.waitFor(5000)
#                         pages_list = await self.browser.pages()
#                         self.page = pages_list[-1]
#                         await self.page.setViewport({"width": 1366, "height": 768})
#                         await self.page.waitFor(3000)
#
#                         # 获取 cookie 并将cookie存入数据库
#                         plats_cookies = await self.get_cookies(account_id)
#                         await self.push_cookies(account_id, shop_id, plats_cookies)
#                         await self.page.waitFor(3000)
#                         await pages_list[-1].close()
#                         await self.page.waitFor(1000)
#                         self.page = pages_list[-2]
#                         return False
#                     else:
#                         if _index == len(account_elements) - 1:
#                             raise Exception(f"{account_name} url地址:agencyAccount,未找到对应的子账号")
#                         else:
#                             continue
#
#             except Exception as e:
#                 import traceback
#                 traceback.print_exc()
#                 self.login_error_type = 2
#                 self.login_error_info = f'错误原因: {e}' if not self.login_error_info else self.login_error_info
#         return True
#
#     async def verify_process(self):
#         """
#         判断是否有滑块并处理
#         Returns:
#         """
#         self.logger.info(f'accountID: {self.shop_info["account_id"]} shopID: {self.shop_info["shop_id"]} 开始处理滑块')
#
#         # 重试次数
#         for i in range(10):
#             try:
#                 if i == 0:
#                     if not await self.page.J('.JDJRV-slide ') and '登录' in await self.page.title():
#                         self.login_status = False
#                         self.login_error_type = 2 if not self.login_error_type else self.login_error_type
#
#                         if await self.page.Jx('//div[contains(text(), "风险")]'):
#                             self.login_error_info = f'accountID: {self.shop_info["account_id"]} 账号存在风险，登陆失败'
#                         else:
#                             self.login_error_info = '自动化程序出错，没有出现滑块，登录失败' if not self.login_error_info else self.login_error_info
#                         raise Exception(self.login_error_info)
#
#                 # 判断是否出现滑块
#                 if await self.page.J('.JDJRV-slide ') and not await self.page.Jx('//div[contains(text(), "风险")]'):
#                     # 获取图片链接
#                     bgd_img_url = await self.page.Jeval('.JDJRV-bigimg > img', 'el => el.src')  # 背景图片
#                     gap_url = await self.page.Jeval('.JDJRV-smallimg > img', 'el => el.src')  # 缺口图片
#
#                     # 下载图片
#                     urlretrieve(bgd_img_url, os.path.join(self.download_path,
#                                                           f"{self.shop_info['account_id']}_{self.plat_type}_bgd.png"))
#                     urlretrieve(gap_url, os.path.join(self.download_path,
#                                                       f"{self.shop_info['account_id']}_{self.plat_type}_gap.png"))
#                     await self.page.waitFor(3000)
#
#                     # 获取滑块边界框
#                     el = await self.page.xpath('//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')
#                     border = await el[0].boundingBox()
#
#                     await self.page.hover('.JDJRV-slide-inner.JDJRV-slide-btn')  # 鼠标悬停滑块按钮
#                     drag_distance = await self.get_distance()  # 灰度匹配获取缺口距离
#
#                     await self.drag_captcha(border, drag_distance + 20)  # 拖拽验证滑块
#                 else:
#                     self.logger.info(f'accountID: {self.shop_info["account_id"]} '
#                                      f'shopID: {self.shop_info["shop_id"]} 滑块校验成功，等待页面跳转')
#                     await self.page.waitFor(3000)  # 等待页面跳转
#                     break
#
#             except Exception as e:
#                 self.login_status = False
#                 self.login_error_type = 1 if not self.login_error_type else self.login_error_type
#                 self.login_error_info = f'自动化处理滑块出错，错误原因: {e}' if not self.login_error_info else self.login_error_info
#
#                 refresh_element = await self.page.Jx('//span[contains(text(), "换一张")]')
#                 await refresh_element[0].click()
#                 await self.page.waitFor(1000)
#         else:
#             raise Exception(self.login_error_info)


async def jd_login():
    jd = JDLogin('用实农资专营店', 'n36389034')
    await jd.browser_operation()


# async def jzt_login():
#     jd = JZTLogin()
#     await jd.run()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(jd_login())
    # asyncio.get_event_loop().run_until_complete(jzt_login())
