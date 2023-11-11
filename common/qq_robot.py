# -*- coding: utf-8 -*-
import hashlib
import json
import random
import time
from typing import List
import requests

from common.common_instantce import CommonInstance


class QQRobot:
    # @staticmethod
    # def send_group_msg(group: int, msg: List):
    #     try:
    #         while CommonInstance.App_IS_LOCKED:
    #             time.sleep(random.randint(5, 15))
    #         CommonInstance.App_IS_LOCKED = True
    #         time.sleep(random.randint(1, 3))
    #         msg = msg[0]
    #         # group = 461936572
    #         url = "http://119.29.97.135:8888/send/group?route=105&frameqq=3266363480&group=%s&key=key&newscontent=%s" % (
    #             group, str(msg.replace('&nbsp;', '').replace('\xa0', ' ').replace('&',"和")))
    #         print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send..',
    #               group, url)
    #         payload = {}
    #         headers = {
    #             'Content-Type': 'multipart/form-data'
    #         }
    #
    #         response = requests.request("POST", url, headers=headers, data=payload)
    #
    #         print(response.text)
    #
    #     except Exception as e:
    #         print('send_group_msg', e)
    #     finally:
    #         requests.session().close()
    #         CommonInstance.App_IS_LOCKED = False
    @staticmethod
    def send_group_msg(group: int, msg: List):
        try:
            while CommonInstance.App_IS_LOCKED:
                time.sleep(random.randint(5, 15))
            CommonInstance.App_IS_LOCKED = True
            time.sleep(random.randint(1, 3))

            url = "https://open.feishu.cn/open-apis/bot/v2/hook/28bb15ff-ca86-4505-9a16-14a39e93a396"
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
        except Exception as e:
            print('send_group_msg', e)
        finally:
            requests.session().close()
            CommonInstance.App_IS_LOCKED = False
