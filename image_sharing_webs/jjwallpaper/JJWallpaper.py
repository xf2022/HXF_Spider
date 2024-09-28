# hxf 2024/6/17
import asyncio
import hashlib
import json
import os.path
import random
import time
from io import BytesIO
from queue import Queue
from threading import Thread

import aiohttp
import arrow
import requests
from PIL import Image, UnidentifiedImageError

import setting
from image_sharing_webs.dao.common_db import MySqlSingleConnect
from image_sharing_webs.dao.image_db import image_insert_sql, verify_image_repeat_sql, image_del_by_id_sql
from image_sharing_webs.logger.common_logger import logger

insert_sql = image_insert_sql
verify_sql = verify_image_repeat_sql
delete_sql = image_del_by_id_sql
DOWNLOAD_PATH = setting.DOWNLOAD_PATH


def get_hash(file):
    """
    :param bytes file:
    :return:
    """
    try:
        md5hash = hashlib.md5(Image.open(file).tobytes())
    # PIL.UnidentifiedImageError: cannot identify image file <_io.BytesIO object at 0x0000020B377C7A60>
    except UnidentifiedImageError as e:
        return ''
    return md5hash.hexdigest()


def exist_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return False
    else:
        return True

def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        return False

class JJWallpaper:
    def __init__(self, business_date=arrow.now().format('YYYY-MM-DD')):
        self.logger = logger
        self.db = MySqlSingleConnect()
        self.business_date = business_date

    def operation(self):
        # 获取图片ID
        # https://api.zzzmh.cn/v2/bz/v3/getData
        # Post
        # form-data
        # {
        #   "size": 24,
        #   "current": 1,
        #   "sort": 0,
        #   "category": 0,
        #   "resolution": 0,
        #   "color": 0,
        #   "categoryId": 0,
        #   "ratio": 0
        # }
        # 返回值 json {
        #     "code": 0,
        #     "message": "success",
        #     "data": {
        #         "currPage": 1,
        #         "list": [
        #             {
        #                 "i": "37aa5dc36d88444786b6b543845963ba",
        #                 "w": 4182,
        #                 "h": 2304,
        #                 "t": 2
        #             },
        #         ],
        #         "pageSize": 24,
        #         "totalCount": 41581,
        #         "totalPage": 1733
        #     }
        # }
        # 下载图片
        # https://api.zzzmh.cn/v2/bz/v3/getUrl/{}
        # Get
        url = 'https://api.zzzmh.cn/v2/bz/v3/getData'
        download_url = 'https://api.zzzmh.cn/v2/bz/v3/getUrl/{}'
        download_path = 'D:\\编程\\python\\HXF_Spider\\图片分享网站\\image\\jjwallpaper\\'
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://bz.zzzmh.cn",
            "Referer": "https://bz.zzzmh.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }
        download_headers = {
            "api.zzzmh.cn": "",
            "GET": "",
            "/v2/bz/v3/getUrl/1b87e2c5880511ebb6edd017c2d2eca219": "",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://bz.zzzmh.cn/",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"117\", \"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"117\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        data_json = {
            "size": 24,
            "current": 1,
            "sort": 0,
            "category": 0,
            "resolution": 0,
            "color": 0,
            "categoryId": 0,
            "ratio": 0
        }
        session = requests.session()
        while True:
            response = session.post(url, json=data_json, headers=headers)
            resp_json = json.loads(response.text)
            if resp_json['code'] == 0:
                data = resp_json['data']
                for list_item in data['list']:
                    print(f"'获取图片: {list_item['i']}'")
                    img_name = list_item['i'] + '_' + arrow.now().format('HH_mm')
                    response = requests.get(download_url.format(list_item['i'] + str(list_item['t']) + '9'))
                    if 'jpeg' in response.headers.get('Content-Type'):
                        img_name += '.jpg'
                    else:
                        img_name += '.png'
                    with open(download_path + img_name, 'wb') as f:
                        f.write(response.content)
                        f.close()
                    time.sleep(2)
                if data['currPage'] < data['pageSize']:
                    data_json['current'] += 1
                else:
                    break
            else:
                print(resp_json['message'])
            print(json.loads(response.text))
        pass

    def run(self):
        url = 'https://api.zzzmh.cn/v2/bz/v3/getData'
        download_url = 'https://api.zzzmh.cn/v2/bz/v3/getUrl/{}'
        download_path = DOWNLOAD_PATH + 'jjwallpaper\\'
        headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://bz.zzzmh.cn",
            "Referer": "https://bz.zzzmh.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }
        download_headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://bz.zzzmh.cn",
            "Referer": "https://bz.zzzmh.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }
        data_json = {
            "size": 96,  # 12 ~ 96
            "current": 1,
            "sort": 0,
            "category": 0,
            "resolution": 0,
            "color": 0,
            "categoryId": 0,
            "ratio": 0
        }
        session = requests.session()

        start_num = 0
        end_num = 1000
        cell_directory_path = download_path + f'{start_num}_{end_num}\\'
        # 当前数量
        current_num = 0

        retry_time = 3
        for i in range(retry_time):
            try:
                while True:
                    # 限制每日获取图片的数量为1000张
                    if current_num >= 1000:
                        break
                    # 判断
                    if exist_dir(cell_directory_path):
                        # 判断，如果文件夹已经满了则创建一个新的文件夹
                        while len(os.listdir(cell_directory_path)) >= 1000:
                            start_num = end_num
                            end_num += 1000
                            cell_directory_path = download_path + f'{start_num}_{end_num}\\'

                            if not exist_dir(cell_directory_path):
                                os.mkdir(cell_directory_path)
                                break
                    else:
                        os.mkdir(cell_directory_path)
                    response = session.post(url, json=data_json, headers=headers)
                    resp_json = json.loads(response.text)
                    # 注意: 请求可能会遭遇反爬或是网络请求问题，需要对其进行处理
                    self.logger.info(f"获取第{data_json['current']}页图片")
                    if response.status_code == 200 and resp_json['code'] == 0:
                        data = resp_json['data']
                        id_list = [img['i'] for img in data['list']]
                        # 判断图片是否都已经存在
                        existed_img_list = self.db.query("select name from hxf_spider.image where owner_id = {} and "
                                                         "`name` in ({})".format(2, "'" + "','".join(id_list) + "'"))
                        existed_img_list = [img[0] for img in existed_img_list]
                        if len(existed_img_list) > 0:
                            self.logger.info(f'图片: {existed_img_list}已存在！')
                        if len(existed_img_list) < len(id_list):
                            for list_item in data['list']:
                                img_name = list_item['i']
                                if img_name in existed_img_list:
                                    continue
                                self.logger.info(f"'获取图片: {list_item['i']}'")
                                # if self.db.query_one(f"select count(1) from hxf_spider.image
                                # where `name` = '{img_name}';")[0]:
                                #     self.logger.warning('图片名-{} 已存在'.format(img_name))
                                #     continue
                                create_time = update_time = arrow.now().format('YYYY-MM-DD hh:mm:ss')
                                insert_data = ['2', '极简壁纸', img_name, f"{list_item['w']}*{list_item['h']}", '', '', '',
                                               '',
                                               '', '', self.business_date, create_time, update_time]
                                response = session.get(download_url.format(list_item['i'] + str(list_item['t']) + '9'),
                                                       headers=download_headers)
                                if response.status_code == 200:
                                    if 'jpeg' in response.headers.get('Content-Type'):
                                        img_name += '.jpg'
                                        insert_data[4] = 'jpg'
                                    else:
                                        img_name += '.png'
                                        insert_data[4] = 'png'
                                    insert_data[6] = cell_directory_path + img_name
                                    hash_code = get_hash(BytesIO(response.content))
                                    insert_data[8] = hash_code
                                    # 判断图片是否已经存在
                                    if self.db.query_one(f"select count(1) from hxf_spider.image "
                                                         f"where `hash` = '{hash_code}';")[0]:
                                        self.logger.warning('图片-{} 已存在'.format(img_name))
                                        continue
                                    with open(cell_directory_path + img_name, 'wb') as f:
                                        f.write(response.content)
                                        f.close()
                                    self.db.insert(insert_sql, insert_data)
                                    time.sleep(2)
                                else:
                                    raise Exception('请求回复状态: ' + str(response.status_code) + ',原因: ' + response.reason)
                        if data['currPage'] < data['totalPage']:
                            data_json['current'] += 1
                        else:
                            total_count = self.db.query_one('select count(1) from hxf_spider.image where owner_id = 2;')
                            if total_count == data['totalCount']:
                                self.logger.info('爬虫任务完成！')
                            else:
                                raise Exception('图片数量不匹配')
                            break
                    else:
                        raise Exception('获取第:' + str(data_json['current']) + '图片数据出错: ' + resp_json['message'])
            except Exception as e:
                self.logger.error(f'爬虫运行出错, 第{i + 1}次重试: {e}')
                if i == 2:
                    raise e
            # print(json.loads(response.text))


class JJWallpaper(object):
    """
    该类用于完成两件事
    1. 下载图片
    2. 保存图片到数据库
    """

    def __init__(self, business_date=arrow.now().format('YYYY-MM-DD')):
        self.img_url = 'https://api.zzzmh.cn/v2/bz/v3/getData'
        self.download_url = 'https://api.zzzmh.cn/v2/bz/v3/getUrl/{}'
        self.img_headers = {
            "Referer": "https://bz.zzzmh.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }
        self.download_headers = {
            "Referer": "https://bz.zzzmh.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }
        self.total_page = 0
        self.total_count = 0
        self.business_date = business_date

        self.first_resp_queue = Queue()
        self.img_url_queue = Queue()

        self.db = MySqlSingleConnect()
        # self.client = aiohttp.ClientSession()

    def get_request_data(self):
        """
        请求页面数据
        :return:
        """
        current = 1
        curr_img = 0
        data_json = {
            "size": 96,  # 12 ~ 96
            "current": 1,
            "sort": 0,
            "category": 0,
            "resolution": 0,
            "color": 0,
            "categoryId": 0,
            "ratio": 0
        }
        while True:
            if current > 0:
                response = requests.post(self.img_url, json=data_json, headers=self.img_headers)
                if response.status_code == 200:
                    resp_json = response.json()
                    if resp_json['message'] == 'success':
                        logger.info('获取第:' + str(current) + '页数据')
                        data = resp_json['data']
                        self.first_resp_queue.put(data)
                        # if current < data['totalPage']:
                        current = data['currPage']
                        curr_img += len(data['list'])
                        if current < 15:
                            current += 1
                            data_json['current'] = current
                            time.sleep(random.randint(400, 800) / 1000)
                        else:
                            logger.info('共获取 {}页数据'.format(current))
                            logger.info('获取图片数据总数: {}'.format(curr_img))
                            self.total_page = data['totalPage']
                            self.total_count = data['totalCount']
                            self.first_resp_queue.put(None)
                            current = -1
            else:
                break

    def parse_first_resp(self):
        while True:
            data = self.first_resp_queue.get()
            # 哨兵
            if data is None:
                self.img_url_queue.put(None)
                break
            logger.info('开始解析第:' + str(data['currPage']) + '页数据')
            img_list = [item['i'] for item in data['list']]
            existed_img_list = [item[0] for item in
                                self.db.query("select name from hxf_spider.image where owner_id = {} and "
                                              "`name` in ({})".format(2, "'" + "','".join(img_list) + "'"))]
            for list_item in data['list']:
                if existed_img_list:
                    if list_item['i'] in existed_img_list:
                        continue
                img_url = self.download_url.format(list_item['i'] + str(list_item['t']) + '9')
                self.img_url_queue.put({'img_url': img_url,
                                        'name': list_item['i'],
                                        'size': f"{list_item['w']}*{list_item['h']}"})
            logger.info(
                '成功解析第{}页共{}张图片，其中{}张图片已存在数据库'.format(data['currPage'], len(data['list']), len(existed_img_list)))

    async def download_img(self, session, img_dict, directory_path):
        """
        下载图片，同时需要返回图片的相关信息
        :param session:
        :param img_dict:
        :param directory_path:
        :return:
        """
        try:
            resp = await session.get(img_dict['img_url'], headers=self.download_headers)
            if resp.status == 200:
                if 'jpeg' in resp.headers.get('Content-Type'):
                    img_dict['img_name'] = img_dict['name'] + '.jpg'
                    img_dict['type'] = 'jpg'
                else:
                    img_dict['img_name'] = img_dict['name'] + '.png'
                    img_dict['type'] = 'png'
                content = await resp.read()
                img_dict['hash'] = get_hash(BytesIO(content))
                img_dict['img_path'] = directory_path + img_dict['img_name']
                with open(img_dict['img_path'], 'wb') as f:
                    f.write(content)
                return resp.status, img_dict
            return resp.status, img_dict

        except Exception as e:
            logger.error('下载图片 {} 报错 {}'.format(img_dict['img_url'], e))

    def save_img_db(self, img_list):
        create_time = update_time = arrow.now().format('YYYY-MM-DD hh:mm:ss')
        hash_tuple = tuple([img_dict['hash'] for img_dict in img_list])
        if len(hash_tuple) == 1:
            repetitive_list = self.db.query(verify_sql % ('(\'' + hash_tuple[0] + '\')'))
        else:
            repetitive_list = self.db.query(verify_sql % str(hash_tuple))
        for (_, name, hash_value, img_path) in repetitive_list:
            for img_dict in img_list:
                if img_dict['hash'] == hash_value:
                    delete_file(img_dict['img_path'])
                    img_list.remove(img_dict)
                    logger.info('图片 {} 已存在数据库, 可自行检查图片'.format(img_path))

        data_list = [
            tuple(
                [2, '极简壁纸', img_dict['name'], img_dict['size'], img_dict['type'], '', img_dict['img_path'], '',
                 img_dict['hash'], '', self.business_date, create_time, update_time]) for img_dict in img_list]
        self.db.insert_many(insert_sql, data_list)

    def save_img(self):
        """
        请求图片下载为异步操作，准备图片url列表，使用异步获取图片，当列表所有的图片获取完毕完成一次循环
        :return:
        """

        async def async_save_img(data_list):
            task_list = []
            img_list = []
            logger.info('{}/{} 图片下载 开始'.format(len(img_list), len(data_list)))
            # 创建异步任务下载图片
            async with aiohttp.ClientSession() as session:
                for img_data in data_list:
                    resp = self.download_img(session, img_data, download_path)
                    task_list.append(asyncio.create_task(resp))
                logger.info('创建下载图片任务 {}个'.format(len(task_list)))
                res_list, _ = await asyncio.wait(task_list)
                for item in res_list:
                    state, img_data = item.result()
                    if state == 200:
                        logger.info('执行下载图片任务 {} 成功'.format(img_data['img_url']))
                        img_list.append(img_data)
                    else:
                        logger.warning('执行下载图片任务 {} 失败'.format(img_data['img_url']))
            logger.info('{}/{} 图片下载 成功！'.format(len(img_list), len(img_data_list)))
            await session.close()
            if img_list:
                self.save_img_db(img_list)

        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)

        download_path = DOWNLOAD_PATH + 'jjwallpaper\\images\\'
        exist_dir(download_path)
        is_done = False
        while not is_done:
            queue_size = self.img_url_queue.qsize()
            if queue_size == 0:
                continue
            img_count = queue_size if queue_size < 10 else 10
            img_data_list = [self.img_url_queue.get() for _ in range(img_count)]
            if img_data_list[-1] is None:
                is_done = True
                img_data_list = img_data_list[:-1]
                if not img_data_list:
                    return

            loop = asyncio.get_event_loop()
            loop.run_until_complete(async_save_img(img_data_list))
            time.sleep(random.randint(400, 800) / 1000)
        thread_loop.close()

    def run(self):
        thread_list = []
        thread_1 = Thread(target=self.get_request_data)
        thread_2 = Thread(target=self.parse_first_resp)
        thread_3 = Thread(target=self.save_img)
        thread_list.extend([thread_1, thread_2, thread_3])
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.save_img())

        for thread in thread_list:
            # 守护进程
            thread.daemon = True
            thread.start()

        for thread in thread_list:
            thread.join()

        logger.info('极简壁纸取数完成！')


if __name__ == '__main__':
    # JJWallpaper().operation()
    # JJWallpaper().run()
    JJWallpaper().run()
