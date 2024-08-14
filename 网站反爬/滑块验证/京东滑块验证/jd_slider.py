import asyncio
import json
import os
import random
import time
from urllib import request

import arrow
import cv2
import pyautogui as pg
import pymysql
import pynput.keyboard
from playwright.async_api import async_playwright

from image_sharing_webs.dao.common_db import MySqlSingleConnect
from 网站反爬.滑块验证.京东滑块验证.get_mouse_position import get_trace

L = []

db = MySqlSingleConnect()

mysql_config = {
    'type': 'mysql',
    'host': 'rm-8vbqu0aw00m93f2c5io.mysql.zhangbei.rds.aliyuncs.com',
    'user': 'root',
    'password': 'Userscrm@2020',
    'dbname': 'ec_spider',
    'port': 3306,
    'charset': 'utf8',
}


async def start_chrome(playwright):
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
    # chrome_path = 'C:\Program Files\Google\Chrome\Application' + '\chrome.exe'
    browser = await playwright.chromium.launch(**launch_dict)
    context = await browser.new_context()
    page = await context.new_page()
    # self.browser = launch(launch_dict, dumpio=True)  # 启动浏览器
    # # 打开新标签页
    # self.page = self.browser.newPage()
    await page.set_viewport_size({"width": 1366, "height": 768})  # 设置网页view大小
    # 读取js文件, 伪装浏览器指纹信息，未使用
    # with open('C:\RPA_ROBOT\EC_Spider\handle\website\dy\stealth.min.js', encoding='utf-8') as f:
    #     js = f.read()
    # await page.add_init_script(path='C:\RPA_ROBOT\EC_Spider\handle\website\dy\js\stealth.min.js')  # 隐藏浏览器指纹
    # 设置？
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {}, }; }''')
    # 设置语言
    await page.evaluate(
        '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    # 设置插件
    await page.evaluate(
        '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    return context, page


async def login_by_cookies(context, page):
    cookies = {
        "__jdu": "1709104002449830912093",
        "TrackID": "1fzJtHiZ5ERrAvGAbqKRnY8Cnoz3739WfrJrNJ-MLJiPUS2v_iScPowEcRrNWmgP0lWwXquWuTFwNSIlNKYG7PTBVZSBrQpoL7xkds3Aip9p5jwZxQiNEKVWm9KWKvp5C",
        "__jdv": "95931165|direct|-|none|-|1716444808057",
        "3AB9D23F7A4B3CSS": "jdd03CL6Z226BCL4XY5QQCAKF6E7XP5BT5R5OSU3D5SWBFSMLY5B4M2RLDXAVWUNFJI4WI3EHACGUT3LQXU2CASCL2VP7NQAAAAMP4JVII2IAAAAADTQYRQ3J2ZJ5U4X",
        "wlfstk_smdl": "yigrte7wx9e6q3r6l6d87hg2zxn9whju",
        "pinId": "6FALg1TEsQj3cLrgIZFVmIyLrn3LzULz",
        "pin": "%E7%94%A8%E5%AE%9E%E5%86%9C%E8%B5%84%E4%B8%93%E8%90%A5%E5%BA%97",
        "__jdc": "227636378",
        "_tp": "8yNPGCLYx%2FrXDOw%2B7wp0E6XpKOR3lP6z8Ob7EadWq%2BWa%2BTglWe11Ia4iupUZgjuKbT1pq1njK4s8K6E60YpNbA%3D%3D",
        "_pst": "%E7%94%A8%E5%AE%9E%E5%86%9C%E8%B5%84%E4%B8%93%E8%90%A5%E5%BA%97",
        "unick": "u22sczv0aew09h",
        "_gia_d": "1",
        "3AB9D23F7A4B3C9B": "CL6Z226BCL4XY5QQCAKF6E7XP5BT5R5OSU3D5SWBFSMLY5B4M2RLDXAVWUNFJI4WI3EHACGUT3LQXU2CASCL2VP7NQ",
        "thor": "3E3B4A7414D05E5398143C93A69DABB842FEED7CE7C544FBA1980CD4415DB6818DBEE94B8C3000E6F6C9241AB0F92F9E6A51E368847594F6CE1975CB166DD0C24CFE7188C3FACD69BD0BB203CA2805F890DB76D17EF4BB00E02C998AADBAE1A07BB6B3FE396031964C75329EBD2FD9FC3DAB5D71A4BB0767A2735C4CDF3288D22FF5DA135B673A281E0AE1E73DE1D7D6",
        "flash": "2_op7rVkh2pAi-khPXPrjbb_GOUrROuBPjlpS7KwsZtbzt_nwS5GG1Pv0HR5J44NNDkytDLzRVA1lPt0HVjch_lviwp70qgOcX8npKbJGEzW9WI-q366prFREQLtSNqrRM3HhSMju9vGjQZWHQ5y25L4l0Pfi4g36P7qiLYPTKd8fK7GRS5iJLavrNYubjcHO1",
        "ceshi3.com": "000",
        "logining": "1",
        "__jda": "227636378.1709104002449830912093.1709104002.1717398768.1717490580.8",
        "__jdb": "227636378.5.1709104002449830912093|8.1717490580"
    }
    for cookie_name in cookies:
        await context.add_cookies([{
            'domain': '.jd_verify.com',
            'name': str(cookie_name).replace(' ', ''),
            'value': cookies[cookie_name],
            'secure': True,
            'httpOnly': False,
            'path': '/',
            'samSite': 'None'
        }])
    await page.goto('https://b.jd.com/')
    await page.wait_for_load_state('load')


def get_conn():
    conn = pymysql.connect(
        host=mysql_config['host'],
        port=mysql_config['port'],
        user=mysql_config['user'],
        password=mysql_config['password'],
        database=mysql_config['dbname'],
        charset=mysql_config['charset']
    )

    return conn


class SliderVerify:
    def __init__(self, page):
        self.db = get_conn().cursor()
        self.page = page
        self.trace = L
        self.press_flag = False
        self.start_time = self.end_time = time.time()
        self.total_time = 0
        self.total_length = 0

    @staticmethod
    def get_position(slider_img, gap_img):
        # 读取图片为cv2
        slider_image = cv2.imread(slider_img)
        gap_image = cv2.imread(gap_img, cv2.IMREAD_UNCHANGED)
        blurred = cv2.GaussianBlur(slider_image, (5, 5), 0, 0)
        slider_canny = cv2.Canny(blurred, 100, 200)
        gap_canny = cv2.Canny(gap_image, 100, 200)
        slider_gray_img = cv2.cvtColor(slider_canny, cv2.COLOR_GRAY2RGB)
        gap_gray_img = cv2.cvtColor(gap_canny, cv2.COLOR_GRAY2RGB)
        cv2.imwrite('./jd_verify/slider_gray.png', slider_gray_img)
        cv2.imwrite('./jd_verify/gap_gray.png', gap_gray_img)
        time.sleep(1)

        # 缺口匹配
        res = cv2.matchTemplate(slider_gray_img, gap_gray_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        th, tw = gap_image.shape[:2]
        tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        cv2.rectangle(slider_image, tl, br, (0, 0, 255), 2)
        cv2.imwrite('./jd_verify/sliver_tangle.png', slider_image)
        return max_loc[0] * 290 / 275

    async def get_tracks(self, distance):
        # tracks, total_length, total_time = get_trace()
        sql = 'select id, trace, length, last_state from slider_trace where ABS(length - {}) < 3 ' \
              'and last_state = True ' \
              'or success_count / (success_count + fail_count ) > 1 / 3 ' \
              'order by ABS(length - {}) ASC;'.format(distance, distance)
        self.db.execute(sql)
        result = self.db.fetchall()
        print(result)
        if len(result) > 0:
            result = [result[0][0], json.loads(result[0][1]), result[0][2]]
            return result
        else:
            print('不存在满足条件的滑块轨迹，需要手动输入')
        return None

    def drag_captcha_with_pyautogui(self, duration: float = 0.4, track_list=None):
        try:
            slider_btn_location = pg.locateOnScreen("D:\\Image\\jd_verify\\slider_btn.png",
                                                    confidence=0.8)
        except Exception as e:
            print('出错了:{}'.format(e))
            raise e
        if not slider_btn_location:
            print('屏幕中没有滑块按钮')
        # slider_ = pg.center(slider_btn_location)
        slider_ = {'x': slider_btn_location.left + random.uniform(14, 56),
                   'y': slider_btn_location.top + random.uniform(14, 56)}
        print(f'按钮位置为: {slider_}')
        cell_time = duration / len(track_list)
        pg.moveTo(slider_['x'], slider_['y'], 1)
        pg.mouseDown()
        first_track = track_list[0]
        j = 0
        track_partition = {
            'start': [3, int(len(track_list) / 4)],
            # 'fast': [4, int(len(track_list) / 4)],
            'mid': [4, int(len(track_list) * 3 / 4)],
            # 'slow': [3, int(len(track_list) / 6)],
            'end': [3, int(len(track_list))],
        }
        for track_part in track_partition:
            step = track_partition[track_part][0]
            for i in range(j + step, track_partition[track_part][1], step):
                j = i
                x = track_list[i]['x'] - first_track['x']
                y = track_list[i]['y'] - first_track['y']
                if track_list[i].get('time'):
                    _time = sum([track['time'] for track in track_list[i - step + 1: i + 1]])
                    print('x: ', x, 'y: ', y, 'time: ', _time)
                    pg.moveTo(slider_['x'] + x, slider_['y'] + y, track_list[i]['time'])
                else:
                    pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time * step)

        _time = sum(track['time'] for track in track_list[j + 1:])
        pg.moveTo(slider_['x'] + track_list[-1]['x'] - first_track['x'],
                  slider_['y'] + track_list[-1]['y'] - first_track['y'], _time)
        time.sleep(random.uniform(0.03, 0.1))
        pg.mouseUp()
        time.sleep(1)

    async def check_verify_(self, item_id):
        """
        处理滑块验证
        :return:
        """
        insert_id = -1
        big_img = 'jd_verify/{}_big_img.png'.format(item_id)
        small_img = 'jd_verify/{}_small_img.png'.format(item_id)
        for i in range(3):  # 循环重试3次
            # 判断是否有验证码图片 并且display为block (如果账号密码错误  完成滑块验证后验证码标签可能并没有消失 display变为none)
            await self.page.wait_for_timeout(1000)
            await self.page.wait_for_load_state('networkidle')
            try:
                print('开始验证')
                if await self.page.query_selector('#captcha_modal'):
                    print('出现滑块')
                    for i in range(10):
                        try:
                            time.sleep(3)
                            await self.page.wait_for_load_state('networkidle')
                            if await self.page.query_selector_all("//*[text()='安全验证']"):
                                big_img_el = await self.page.query_selector('#captcha_modal #cpc_img')
                                big_img_src = await big_img_el.get_attribute('src')  # 获取大图
                                big_img_path = os.path.join(os.getcwd(), big_img)
                                request.urlretrieve(big_img_src, big_img_path)

                                small_img_el = await self.page.query_selector('#captcha_modal #small_img')
                                small_img_src = await small_img_el.get_attribute('src')
                                small_img_path = os.path.join(os.getcwd(), small_img)
                                request.urlretrieve(small_img_src, small_img_path)
                                time.sleep(3)

                                if insert_id >= 0:
                                    sql = 'update slider_trace set last_state = False, fail_count = fail_count + 1 ' \
                                          'where id = %s'
                                    self.db.execute(sql, (insert_id,))

                                distance = get_position(big_img, small_img)
                                print('distance: {}'.format(distance))
                                result = await get_tracks(distance)
                                if result:
                                    insert_id = result[0]
                                    print(result[2], distance)
                                    drag_captcha_with_pyautogui(track_list=result[1])
                                else:
                                    sql = 'insert into slider_trace (url, length, time, trace, create_time, update_time) ' \
                                          'values (%s, %s, %s, %s, %s, %s)'
                                    track, total_length, total_time = get_trace()
                                    curr_time = arrow.now()
                                    if total_length < 60 or total_length > 330:
                                        print('轨迹出现问题')
                                        insert_id = -1
                                        continue
                                    insert_id = self.db.execute(sql, (
                                        "https://cfe.m.jd.com", distance, total_time, json.dumps(track),
                                        curr_time, curr_time))
                                    print('轨迹入库, id: {}'.format(insert_id))
                            else:
                                sql = 'update slider_trace set last_state = True, success_count = success_count + 1 ' \
                                      'where id = %s'
                                self.db.execute(sql, (insert_id,))
                                break
                        except Exception as e:
                            print('出错了 {}'.format(e), end='')
                else:
                    break
            except Exception as e:
                print('出错了 {}'.format(e), end='')
                if i < 2:
                    print('重新尝试!')
                    self.page.reload()
                else:
                    print('')
        return not await self.page.query_selector('#captcha_modal')  # 返回图片验证是否还在页面上

    def _on_move(self, x, y):
        self.end_time = time.time()
        if self.press_flag:
            # print('鼠标位置: {}'.format((x, y)))
            diff_time = self.end_time - self.start_time
            if diff_time > 0.02 and self.press_flag:
                point = {'x': x, 'y': y, 'time': diff_time}
                self.trace.append(point)
                print('鼠标当前位置: {}'.format(point))
                self.total_time += diff_time
                self.start_time = time.time()

    def _on_click(self, x, y, button, pressed):
        # 监听鼠标点击
        if pressed:
            print("鼠标点击")
            mxy = "{},{}".format(x, y)
            print(mxy)
            print(button)
            self.press_flag = True
            self.trace.append({'x': x, 'y': y, 'time': 0.0})
            self.start_time = time.time()
            # return False
        if not pressed:
            print("鼠标释放")
            mxy = "{},{}".format(x, y)
            # Stop listener
            self.press_flag = False
            self.end_time = time.time()
            self.trace.append({'x': x, 'y': y, 'time': self.end_time - self.start_time})
            self.total_time += self.end_time - self.start_time
            self.total_length = self.trace[-1]['x'] - self.trace[0]['x']
            print('total_length: {}  total_time: {}'.format(self.total_length, self.total_time))
            return False

    def get_trace(self):
        self.trace = []
        self.total_time = self.total_length = 0
        with pynput.mouse.Listener(on_click=self._on_click, on_move=self._on_move) as listener:
            listener.join()
        return self.trace, self.total_length, self.total_time


def get_position(slider_img, gap_img):
    # 读取图片为cv2
    slider_image = cv2.imread(slider_img)
    gap_image = cv2.imread(gap_img, cv2.IMREAD_UNCHANGED)
    blurred = cv2.GaussianBlur(slider_image, (5, 5), 0, 0)
    slider_canny = cv2.Canny(blurred, 100, 200)
    gap_canny = cv2.Canny(gap_image, 100, 200)
    slider_gray_img = cv2.cvtColor(slider_canny, cv2.COLOR_GRAY2RGB)
    gap_gray_img = cv2.cvtColor(gap_canny, cv2.COLOR_GRAY2RGB)
    cv2.imwrite('./jd_verify/slider_gray.png', slider_gray_img)
    cv2.imwrite('./jd_verify/gap_gray.png', gap_gray_img)
    time.sleep(1)

    # 缺口匹配
    res = cv2.matchTemplate(slider_gray_img, gap_gray_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    th, tw = gap_image.shape[:2]
    tl = max_loc
    br = (tl[0] + tw, tl[1] + th)
    cv2.rectangle(slider_image, tl, br, (0, 0, 255), 2)
    cv2.imwrite('./jd_verify/sliver_tangle.png', slider_image)
    return max_loc[0] * 290 / 275


async def get_tracks(distance):
    # tracks, total_length, total_time = get_trace()
    sql = 'select id, trace, length, last_state from slider_trace where ABS(length - {}) < 3 and last_state = True ' \
          'order by ABS(length - {}) ASC;'.format(distance, distance)
    result = db.query(sql)
    print(result)
    if len(result) > 0:
        result = [result[0][0], json.loads(result[0][1]), result[0][2]]
        return result
    else:
        print('不存在满足条件的滑块轨迹，需要手动输入')
    return None


def drag_captcha_with_pyautogui(duration: float = 0.4, track_list=None):
    try:
        slider_btn_location = pg.locateOnScreen("D:\\Image\\jd_verify\\slider_btn.png",
                                                confidence=0.8)
    except Exception as e:
        print('出错了:{}'.format(e))
        raise e
    if not slider_btn_location:
        print('屏幕中没有滑块按钮')
    # slider_ = pg.center(slider_btn_location)
    slider_ = {'x': slider_btn_location.left + random.uniform(14, 56),
               'y': slider_btn_location.top + random.uniform(14, 56)}
    print(f'按钮位置为: {slider_}')
    cell_time = duration / len(track_list)
    pg.moveTo(slider_['x'], slider_['y'], 1)
    pg.mouseDown()
    first_track = track_list[0]
    j = 0
    track_partition = {
        'start': [3, int(len(track_list) / 4)],
        # 'fast': [4, int(len(track_list) / 4)],
        'mid': [4, int(len(track_list) * 3 / 4)],
        # 'slow': [3, int(len(track_list) / 6)],
        'end': [3, int(len(track_list))],
    }
    for track_part in track_partition:
        step = track_partition[track_part][0]
        for i in range(j + step, track_partition[track_part][1], step):
            j = i
            x = track_list[i]['x'] - first_track['x']
            y = track_list[i]['y'] - first_track['y']
            if track_list[i].get('time'):
                _time = sum([track['time'] for track in track_list[i - step + 1: i + 1]])
                print('x: ', x, 'y: ', y, 'time: ', _time)
                pg.moveTo(slider_['x'] + x, slider_['y'] + y, track_list[i]['time'])
            else:
                pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time * step)

    # fast_part = int(len(track_list) * 3 / 5)
    # middle_part = int(len(track_list) * 4 / 5)
    # # slow_part = len(track_list) - fast_part
    # for i in range(j + 4, fast_part, 4):
    #     j = i
    #     x = track_list[i]['x'] - first_track['x']
    #     y = track_list[i]['y'] - first_track['y']
    #     print('x: ', x, 'y: ', y)
    #     if track_list[i].get('time'):
    #         _time = sum(track['time'] for track in track_list[i-3:i+1])
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, track_list[i]['time'])
    #     else:
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time * 4)
    # for i in range(j + 5, middle_part, 5):
    #     j = i
    #     x = track_list[i]['x'] - first_track['x']
    #     y = track_list[i]['y'] - first_track['y']
    #     print('x: ', x, 'y: ', y)
    #     if track_list[i].get('time'):
    #         _time = sum(track['time'] for track in track_list[i-4:i+1])
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, track_list[i]['time'])
    #     else:
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time * 5)
    # for i in range(j + 3, len(track_list), 3):
    #     j = i
    #     x = track_list[i]['x'] - first_track['x']
    #     y = track_list[i]['y'] - first_track['y']
    #     print('x: ', x, 'y: ', y)
    #     if track_list[i].get('time'):
    #         _time = sum(track['time'] for track in track_list[i-2:i+1])
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, track_list[i]['time'])
    #     else:
    #         pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time * 3)

    _time = sum(track['time'] for track in track_list[j + 1:])
    pg.moveTo(slider_['x'] + track_list[-1]['x'] - first_track['x'],
              slider_['y'] + track_list[-1]['y'] - first_track['y'], _time)
    # else:
    #     for track in track_list[1:]:
    #         x = track['x'] - first_track['x']
    #         y = track['y'] - first_track['y']
    #         print('x: ', x, 'y: ', y)
    #         if track.get('time'):
    #             pg.moveTo(slider_['x'] + x, slider_['y'] + y, track['time'])
    #         else:
    #             pg.moveTo(slider_['x'] + x, slider_['y'] + y, cell_time)
    # pg.moveTo(slider_.x + x + track_list[-1]['x'], slider_.y + y + track_list[-1]['y'], random.uniform(0.8, 1))
    time.sleep(random.uniform(0.03, 0.1))
    pg.mouseUp()
    time.sleep(1)


count = 0


async def check_verify_(page, item_id):
    """
    处理滑块验证
    :return:
    """
    global count
    insert_id = -1
    count = 0
    big_img = 'jd_verify/{}_big_img.png'.format(item_id)
    small_img = 'jd_verify/{}_small_img.png'.format(item_id)
    for i in range(3):  # 循环重试3次
        # 判断是否有验证码图片 并且display为block (如果账号密码错误  完成滑块验证后验证码标签可能并没有消失 display变为none)
        await page.wait_for_timeout(1000)
        await page.wait_for_load_state('networkidle')
        try:
            print('开始验证')
            if await page.query_selector('#captcha_modal'):
                print('出现滑块')
                for i in range(10):
                    try:
                        time.sleep(3)
                        await page.wait_for_load_state('networkidle')
                        if await page.query_selector_all("//*[text()='安全验证']"):
                            big_img_el = await page.query_selector('#captcha_modal #cpc_img')
                            big_img_src = await big_img_el.get_attribute('src')  # 获取大图
                            big_img_path = os.path.join(os.getcwd(), big_img)
                            request.urlretrieve(big_img_src, big_img_path)

                            small_img_el = await page.query_selector('#captcha_modal #small_img')
                            small_img_src = await small_img_el.get_attribute('src')
                            small_img_path = os.path.join(os.getcwd(), small_img)
                            request.urlretrieve(small_img_src, small_img_path)
                            time.sleep(3)

                            if insert_id >= 0:
                                sql = 'update slider_trace set last_state = False, fail_count = fail_count + 1 ' \
                                      'where id = %s'
                                db.exec_one(sql, (insert_id,))

                            distance = get_position(big_img, small_img)
                            print('distance: {}'.format(distance))
                            result = await get_tracks(distance)
                            if result:
                                insert_id = result[0]
                                print(result[2], distance)
                                drag_captcha_with_pyautogui(track_list=result[1])
                            else:
                                sql = 'insert into slider_trace (url, length, time, trace, create_time, update_time) ' \
                                      'values (%s, %s, %s, %s, %s, %s)'
                                track, total_length, total_time = get_trace()
                                curr_time = arrow.now()
                                if total_length < 60 or total_length > 330:
                                    print('轨迹出现问题')
                                    insert_id = -1
                                    continue
                                insert_id = db.insert(sql, (
                                    "https://cfe.m.jd.com", distance, total_time, json.dumps(track),
                                    curr_time, curr_time))
                                print('轨迹入库, id: {}'.format(insert_id))
                        else:
                            sql = 'update slider_trace set last_state = True, success_count = success_count + 1 ' \
                                  'where id = %s'
                            db.exec_one(sql, (insert_id,))
                            break
                    except Exception as e:
                        await page.goto(
                            'https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?returnurl=https%3A%2F%2Fitem.jd'
                            '.com%2F100076347570.html&evtype=2&rpid=rp-188105046-10134-1717404228495#crumb-wrap')
            else:
                break
        except Exception as e:
            print('出错了 {}'.format(e), end='')
            if i < 2:
                print('重新尝试!')
                page.reload()
            else:
                print('')
    return not await page.query_selector('#captcha_modal')  # 返回图片验证是否还在页面上


exit_flag = False


async def handle_verify_test():
    playwright = await async_playwright().start()
    context, page = await start_chrome(playwright)

    await login_by_cookies(context, page)

    def on_press(key):
        global exit_flag
        if key == 'esc':
            exit_flag = True
            return False

    with pynput.keyboard.Listener(on_press=on_press) as listener:
        while not exit_flag:
            await page.goto(
                'https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?returnurl=https%3A%2F%2Fitem.jd.com'
                '%2F100076347570.html&evtype=2&rpid=rp-188105046-10134-1717404228495#crumb-wrap')
            verify_btn = await page.query_selector("//*[text()='快速验证']")
            await verify_btn.click()
            await page.wait_for_timeout(1000)
            result = await check_verify_(page, 1)
            if result:
                print('验证成功！')
            else:
                print('验证失败')
        listener.join()

    time.sleep(15)

async def handle_slider_verify_test():
    playwright = await async_playwright().start()
    context, page = await start_chrome(playwright)
    await page.goto(
        'https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?returnurl=https%3A%2F%2Fitem.jd.com'
        '%2F100076347570.html&evtype=2&rpid=rp-188105046-10134-1717404228495#crumb-wrap')
    verify_btn = await page.query_selector("//*[text()='快速验证']")
    await verify_btn.click()
    slider_verify = SliderVerify(page)

    slider_verify.db.execute('select * from slider_trace')
    print(slider_verify.db.fetchall())
    await slider_verify.check_verify_(1)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(handle_verify_test())
    # asyncio.get_event_loop().run_until_complete(handle_slider_verify_test())

    pass
