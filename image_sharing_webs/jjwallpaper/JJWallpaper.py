# hxf 2024/6/17
import hashlib
import json
import os.path
import time
from io import BytesIO

import arrow
import requests
from PIL import Image, UnidentifiedImageError

import setting
from image_sharing_webs.dao.common_db import MySqlSingleConnect
from image_sharing_webs.dao.image_db import image_insert_sql
from image_sharing_webs.logger.common_logger import logger

insert_sql = image_insert_sql
DOMNLOAD_PATH = setting.DOMNLOAD_PATH


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
        download_path = DOMNLOAD_PATH + 'jjwallpaper\\'
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
                                insert_data = ['2', '极简壁纸', img_name, f"{list_item['w']}*{list_item['h']}", '', '', '', '',
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


if __name__ == '__main__':
    # JJWallpaper().operation()
    JJWallpaper().run()
