# -*- coding: utf-8 -*-
import hashlib
import json
import random
import time
from typing import List
import requests

from common.common_instantce import CommonInstance


class QQRobot:

    @staticmethod
    def send_group_msg(group: int, msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/28bb15ff-ca86-4505-9a16-14a39e93a396"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_blogs(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/04e4b871-2a41-4fb7-b141-cb8b697abffa"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_to_coding(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/c8381e3c-e9cd-41de-829e-3bb09dd6bcb6"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_to_police(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/2b904c87-8c76-4f5f-bd65-0940bc09d6f0"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_to_idea(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/51b20808-6df1-49c3-8fc4-ec32217699c4"
        QQRobot.common_send(url, msg)

    @staticmethod
    def common_send(url, msg: List):
        try:
            while CommonInstance.App_IS_LOCKED:
                time.sleep(random.randint(5, 15))
            CommonInstance.App_IS_LOCKED = True
            time.sleep(random.randint(1, 3))

            payload = {"msg_type": "text",
                       "content": {"text": str(msg[0]), }}
            data = json.dumps(payload)

            # 按照utf-8编码成字节码
            data = data.encode("utf-8")
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=data)
            print(response.text)

            QQRobot.send_to_es(str(msg[0]))
        except Exception as e:
            print('send_group_msg', e)
        finally:
            requests.session().close()
            CommonInstance.App_IS_LOCKED = False

    @staticmethod
    def send_to_es(msg):
        curr_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        payload = {"msg": msg,
                   "create_time": curr_date}
        data = json.dumps(payload)

        # 按照utf-8编码成字节码
        data = data.encode("utf-8")
        headers = {
            'Content-Type': 'application/json'
        }
        url = 'http://inner.tacbin.club:9200/spider/_doc'
        response = requests.request("POST", url, headers=headers, data=data)
        print(response.text)
