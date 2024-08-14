import asyncio
import os
import random
import time
from urllib.request import urlretrieve

import cv2
import numpy as np
from playwright.async_api import async_playwright

from 商品网站.JD.jd_auto_login import JDLogin
from 网站反爬.super_eagle_verify import LoginClient, config
from 网站反爬.滑块验证.京东滑块验证.jd_slider import start_chrome


class CheckImageVerify:
    def __init__(self, page, item_id, download_path):
        self.login_status = self.login_error_type = self.login_error_info = None
        self.page = page
        self.item_id = item_id
        self.download_path = download_path

    async def send_verify_image(self, item_id):
        """
        发送合并好的图片给超级鹰，返回坐标字符串
        Returns:
        """
        super_eagle = LoginClient(config['user'], config['password'], config['program_id'])
        verify_image = open(self.download_path + '{}_check_img_screenshot.png'.format(item_id), 'rb').read()
        response = super_eagle.PostPic(verify_image, 9101)  # 返回坐标字符串 'x1,y1'

        if '题分' in response['err_str']:
            self.login_status = False
            self.login_error_type = 1
            self.login_error_info = f'超级鹰余额不足，无法处理验证码，登录失败'
            raise Exception(self.login_error_info)
        else:
            location_str = response['pic_str']
            return location_str.split(',')

    async def check_verify_(self):
        """
        处理滑块验证
        :return:
        """
        # self.check_img_path()
        for i in range(3):  # 循环重试5次
            # 判断是否有验证码图片 并且display为block (如果账号密码错误  完成滑块验证后验证码标签可能并没有消失 display变为none)
            try:
                modal = await self.page.query_selector('#captcha_modal')
                if modal:
                    await modal.screenshot(path=self.download_path + f'{self.item_id}_screenshot.png')

                    location = await self.send_verify_image(self.item_id)  # 发送图片，接收坐标

                    # 定位提示图片位置后，点击验证码
                    await self.page.hover('#captcha_modal')  # 移动到提示框，显示验证图
                    await self.page.wait_for_timeout(1000)

                    verify_img_element = await self.page.query_selector('#captcha_modal')
                    element_box = await verify_img_element.bounding_box()
                    await self.page.mouse.click(element_box['x'] + int(location[0]),
                                                element_box['y'] + int(location[1]))

                    await self.page.wait_for_timeout(1000)
                else:
                    break
            except Exception as e:
                # logger.error('验证出错了! {}'.format(e))
                time.sleep(10)
        await self.page.wait_for_timeout(3000)
        return not await self.page.query_selector('#captcha_modal')  # 返回图片验证是否还在页面上


class JDLogin:

    def __init__(self, account_id, account_pwd, playwright):
        self.account_id = account_id
        self.account_pwd = account_pwd
        self.download_path = "D:/Image/jd_login/"  # 不能够出现中文
        # self.logger = get_stream_logger('jd_login')

        self.playwright = playwright
        self.browser = None
        self.context = None
        self.page = None

    async def start_chrome(self):

        chrome_args_list = [
            '--no-sandbox',  # 不使用沙盒
            # '--start-maximized',  # 允许网络安全
            '--window-size=1366,768',  # 浏览器大小
            '--disable-blink-features=AutomationControlled',  # 屏蔽webdriver特征
            '--disable-infobars',  #
            # '--user-data-dir="F:/RPAData/test01"',  # 浏览器user-data-dir 参数
        ]
        launch_dict = {
            # "executablePath": "C:\Program Files\Google\Chrome\Application\chrome.exe",  # 浏览器启动地址
            'headless': False,  # 不使用无头模式
            'args': chrome_args_list,
            # "ignoreHTTPSErrors": True,  # 忽略https错误
            # "ignoreDefaultArgs": ["--enable-automation"]
            # 'dumpio': True
        }
        # chrome_path = check_chrome_path() + '\chrome.exe'
        chrome_path = r'C:\Users\HXF\AppData\Local\Google\Chrome\Application\chrome.exe'
        self.browser = await self.playwright.chromium.launch(**launch_dict,
                                                             executable_path=chrome_path)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.set_viewport_size({"width": 1366, "height": 768})  # 设置网页view大小

        # 设置？
        await self.page.evaluate('''() =>{ window.navigator.chrome = { runtime: {}, }; }''')
        # 设置语言
        await self.page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
        # 设置插件
        await self.page.evaluate(
            '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

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

        await self.start_chrome()

        # 登录重试3次
        for i in range(3):
            try:
                # 开始登录操作
                await self.page.goto('https://passport.jd.com/new/login.aspx?ReturnUrl=https://vc.jd.com')

                # 输入账号密码
                await self.page.click('#loginname.itxt')
                await self.page.evaluate('document.querySelector("#loginname.itxt").value=""')
                await self.page.type('#loginname.itxt', shop_account, delay=random.randint(60, 121))  # 账号

                await self.page.click('#nloginpwd.itxt.itxt-error')
                await self.page.type('#nloginpwd.itxt.itxt-error', shop_password, delay=random.randint(100, 151))  # 密码

                if 'login' in self.page.url:
                    await self.page.click('.login-btn')
                    await self.page.wait_for_timeout(5000)

                    # 校验滑块验证码
                    await self.verify_process()
                    # 校验登录状态
                    await self.check_login_status()
                break
            except Exception as e:
                await self.browser.close()  # 关闭浏览器
                self.login_status = True  # 重试时重置登录状态
                self.login_error_type = 4 if not self.login_error_type else self.login_error_type
                self.login_error_info = f'任务过程出错，错误原因为: {e}' if not self.login_error_info else self.login_error_info
        else:
            self.login_status = False  # 重试次数用完后，标记登录状态为失败
            raise

    async def verify_process(self):
        """
        判断是否有滑块并处理
        Returns:
        """
        # 重试次数
        for i in range(10):
            try:
                if i == 0:
                    if not await self.page.query_selector_all('.JDJRV-slide') and '登录' in await self.page.title():
                        self.login_status = False
                        self.login_error_type = 2 if not self.login_error_type else self.login_error_type

                        if await self.page.query_selector_all('//div[contains(text(), "风险")]'):
                            self.login_error_info = f'accountID: {self.account_id} 账号存在风险，登陆失败'
                        else:
                            self.login_error_info = '自动化程序出错，没有出现滑块，登录失败' if not self.login_error_info else self.login_error_info
                        raise Exception(self.login_error_info)

                # 判断是否出现滑块
                if await self.page.query_selector_all('.JDJRV-slide ') and not await self.page.query_selector_all(
                        '//div[contains(text(), "风险")]'):
                    # 获取图片链接
                    bgd_img_el = await self.page.query_selector('.JDJRV-bigimg > img')  # 背景图片
                    bgd_img_url = await bgd_img_el.get_attribute('src')
                    gap_el = await self.page.query_selector('.JDJRV-smallimg > img')  # 缺口图片
                    gap_url = await gap_el.get_attribute('src')

                    # 下载图片
                    urlretrieve(bgd_img_url, os.path.join(self.download_path,
                                                          f"jd_login_bgd.png"))
                    urlretrieve(gap_url, os.path.join(self.download_path,
                                                      f"jd_login_gap.png"))
                    await self.page.wait_for_timeout(3000)

                    # 获取滑块边界框
                    el = await self.page.query_selector_all('//div[@class="JDJRV-slide-inner JDJRV-slide-btn"]')
                    border = await el[0].bounding_box()

                    await self.page.hover('.JDJRV-slide-inner.JDJRV-slide-btn')  # 鼠标悬停滑块按钮
                    drag_distance = await self.get_distance()  # 灰度匹配获取缺口距离
                    await self.drag_captcha(border, drag_distance + 20)  # 拖拽验证滑块
                else:

                    break
                await self.page.wait_for_timeout(3000)  # 等待页面跳转

            except Exception as e:
                self.login_status = False
                self.login_error_type = 1 if not self.login_error_type else self.login_error_type
                self.login_error_info = f'自动化处理滑块出错，错误原因: {e}' if not self.login_error_info else self.login_error_info

                refresh_element = await self.page.query_selector_all('//span[contains(text(), "换一张")]')
                await refresh_element[0].click()
                await self.page.wait_for_timeout(1000)
        else:
            raise Exception(self.login_error_info)

    async def get_distance(self):
        """
        使用 cv2 库 灰度匹配获取缺口距离
        Returns:
        """
        bgd_img = cv2.imread(
            os.path.join(self.download_path, f'jd_login_bgd.png'), 0)
        gap_img = cv2.imread(
            os.path.join(self.download_path, f'jd_login_gap.png'), 0)
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
            await self.page.mouse.move(border['x'] + drag_distance + random.uniform(30, 33), border['y'], steps=30)
            await self.page.wait_for_timeout(random.randint(300, 700))
            await self.page.mouse.move(border['x'] + drag_distance + 16, border['y'], steps=30)
            await self.page.mouse.up()
            await self.page.wait_for_timeout(3000)
        except Exception as e:
            self.login_status = False
            self.login_error_info = f'处理滑块出错，错误原因为: {e}'
            raise

    async def check_login_status(self):
        """
        校验登录状态
        Returns:
        """
        await self.page.wait_for_timeout(3000)
        print('网页标题:', await self.page.title())
        if '登录' in await self.page.title():
            self.login_status = False
            self.login_error_type = 2

            if await self.page.query_selector_all('//div[contains(text(), "风险")]'):
                self.login_error_info = f'accountID: {self.account_id} 账号存在风险，登陆失败'
            else:
                self.login_error_info = '登录没有成功跳转页面，登录失败'
            raise Exception(self.login_error_info)
        elif '验证' in await self.page.title() or '认证' in await self.page.title():
            self.login_status = False
            self.login_error_type = 3
            self.login_error_info = f'accountID: {self.account_id} 需要验证码，登陆失败'
            # raise Exception(self.login_error_info)
            while '验证' in await self.page.title() or '认证' in await self.page.title():
                await self.page.wait_for_timeout(1000)

        # logger.info(f'accountID: {self.account_id} '
        #             f'跳转页面成功，准备获取cookie')
        return True


async def verify_test():
    playwright = await async_playwright().start()
    # context, page = await start_chrome(playwright)
    login = JDLogin('18028674500', 'user@2024', playwright)
    await login.browser_operation()
    while True:
        await login.page.goto(
            'https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?returnurl=https%3A%2F%2Fitem.jd.com%'
            '2F100031331880.html&evtype=2&rpid=rp-191096440-10368-1719289721514#crumb-wrap')
        verify_btn = await login.page.query_selector("//*[text()='快速验证']")
        await verify_btn.click()
        await login.page.wait_for_timeout(1000)
        if await CheckImageVerify(login.page, 1).check_verify_():
            print('验证成功！')
        else:
            print('验证失败')


if __name__ == '__main__':
    os.chdir(r'D:\编程\python\HXF_Spider')
    asyncio.get_event_loop().run_until_complete(verify_test())
