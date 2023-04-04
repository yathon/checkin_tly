# -*- coding: utf-8 -*-
import os
import base64
import io
import json
import logging
import re
import time

import requests
from PIL import Image

import ocr
from RobotNotice.RobotNotice import notice


domain = os.environ["DOMAIN"]
user = os.environ["USER"]
pwd = os.environ["PWD"]
key = os.environ["KEY"]
robot = os.environ["ROBOT"]
robot_key = os.environ["ROBOT_KEY"]

TEMP_PATH = '/tmp'
logging.basicConfig(level='DEBUG', format='[%(asctime)s][%(levelname)s] %(message)s')


class Checkin:

    def __init__(self):
        self.Login_url = f"https://{domain}/modules/_login.php"
        self.captcha_url = f"https://{domain}/other/captcha.php"
        self.Login_data = {
            'email': self._d(user, key),
            'passwd': self._d(pwd, key),
            'remember_me': 'week'
        }
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/75.0.3739.0 Safari/537.36 Edg/75.0.111.0 "
        }
        self.count_number = 0
        self.session = requests.session()

    def captcha_main(self, image_data):
        yzm = self.captcha_ocr(image_data)
        if yzm and len(yzm) == 4:
            return yzm

    @staticmethod
    def binazing(image_data):
        image = Image.open(io.BytesIO(image_data))
        # 灰度化
        image = image.convert('L')
        # 增强对比度
        image = image.point(lambda x: 1.2 * x)
        w, h = image.size
        # 二值化
        pixdata = image.load()
        for i in range(h):
            for j in range(w):
                if pixdata[j, i] > 180:
                    pixdata[j, i] = 255
                else:
                    pixdata[j, i] = 0
        image.save(f'{TEMP_PATH}/captcha.png')

    def captcha_ocr(self, image_data):
        self.binazing(image_data)
        with open(f'{TEMP_PATH}/captcha.png', 'rb') as f:
            image_data = f.read()
        _ocr = ocr.Ocr()
        code = _ocr.classification(image_data)
        return code

    @staticmethod
    def _e(e, k):
        return base64.standard_b64encode(f'{e}{k}'.encode()).decode()

    @staticmethod
    def _d(e, k):
        tmp = base64.standard_b64decode(e).decode()
        return tmp.replace(k, '')

    @staticmethod
    def has_chs(msg):
        return len(re.findall('[\u4e00-\u9fa5]', msg)) > 0

    def get_cat(self):
        try:
            self.count_number += 1
            content = self.session.get(self.captcha_url.format(), headers=self.header).content
            yzm = self.captcha_main(content)
            if not yzm or len(yzm) != 4 or self.has_chs(yzm):
                if self.count_number < 50:
                    time.sleep(3)
                    return self.get_cat()
                else:
                    info = f'[{robot_key}]我已经尽力了，你自己想办法吧'
                    logging.error(info)
                    notice(info, robot)
                return False
            logging.info(f'识别的验证码： {yzm}')
            code_url = 'https://' + domain + '/modules/_checkin.php?captcha=' + yzm
            # print(code_url)
            data = self.session.get(str(code_url), headers=self.header)
            result = re.findall(r'<script>alert(.*);self.location=document.referrer;</script>', data.text)
            msg = result[0]
            info = f'[{robot_key}][{yzm}] {msg}'
            logging.info(info)
            notice(info, robot)
            if msg == "('验证码错误!')" and self.count_number < 50:
                time.sleep(3)
                return self.get_cat()
            self.count_number = 0
            return True
        except Exception as e:
            logging.error(f'Project_Error: {e}')
        return False

    def login(self):
        try:
            html = self.session.post(self.Login_url.format(), data=self.Login_data,
                                     headers=self.header, timeout=30)
            html.encoding = html.apparent_encoding
            login_data = json.loads(html.text)
            # logger(login_data)
            if login_data['ok'] == '1':
                logging.info('Login_Ok!')
                return self.get_cat()
        except Exception as e:
            logging.error(f'Login_Error: {e}')
        return False

    def run(self):
        success_day = None
        while True:
            today = time.strftime("%Y%m%d")
            cur_hm = time.strftime("%H%M")
            if success_day != today and cur_hm >= '0901':
                logging.info('start to check in')
                logging.info(f'domain: {domain}')
                if self.login():
                    success_day = today
            time.sleep(60)


if __name__ == '__main__':
    ckn = Checkin()
    # ckn.run()
    ckn.login()
