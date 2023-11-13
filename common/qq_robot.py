# -*- coding: utf-8 -*-
import hashlib
import json
import random
import time
from typing import List
import requests
# pip install requests_toolbelt
from requests_toolbelt import MultipartEncoder

from common.common_instantce import CommonInstance


class QQRobot:

    # https://open.feishu.cn/api-explorer/cli_a5d8f9b46b78500b?apiName=create&from=op_doc_tab&project=im&resource=image&version=v1
    @staticmethod
    def upload_msg_image(file_path):
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        form = {'image_type': 'message',
                'image': (open(file_path, 'rb'))}  # 需要替换具体的path
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': 'Bearer t-g104bdnPBR7TRYO7RA65JHYR5ZVGGF6HRLFOJR5B',
            ## 获取tenant_access_token, 需要替换为实际的token
        }
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form)
        print(response.headers['X-Tt-Logid'])  # for debug or oncall
        print(response.content)
        import ast
        map = ast.literal_eval(str(response.content, encoding = "utf-8"))
        return map['data']['image_key']

    @staticmethod
    def send_group_msg(group: int, msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/28bb15ff-ca86-4505-9a16-14a39e93a396"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_blogs(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/04e4b871-2a41-4fb7-b141-cb8b697abffa"
        QQRobot.common_send(url, msg)

    @staticmethod
    def send_image_blogs(msg: List):
        url = "https://open.feishu.cn/open-apis/bot/v2/hook/04e4b871-2a41-4fb7-b141-cb8b697abffa"
        QQRobot.common_send_image(url, msg)

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
    def common_send_image(url, msg: List):
        try:
            while CommonInstance.App_IS_LOCKED:
                time.sleep(random.randint(5, 15))
            CommonInstance.App_IS_LOCKED = True
            time.sleep(random.randint(1, 3))
            img_key = QQRobot.upload_msg_image(msg[0])

            # 发送图片消息
            payload = {"msg_type": "image",
                       "content": {"image_key": img_key, }}
            data = json.dumps(payload)

            # 按照utf-8编码成字节码
            data = data.encode("utf-8")
            headers = {
                'Authorization': 'Bearer ' + 't-g104bdnPBR7TRYO7RA65JHYR5ZVGGF6HRLFOJR5B'
            }
            response = requests.request("POST", url, headers=headers, data=data)
            print(response.text)

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
