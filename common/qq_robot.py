# -*- coding: utf-8 -*-
import random
import time
from typing import List

from common.common_instantce import CommonInstance


class QQRobot:
    @staticmethod
    def send_group_msg(group: int, msg: List):
        try:
            while CommonInstance.App_IS_LOCKED:
                time.sleep(random.randint(5, 15))
            CommonInstance.App_IS_LOCKED = True
            time.sleep(random.randint(1, 3))
            msg = msg[0]
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send..',
                  group, msg)

            import requests

            url = "http://119.29.97.135:8888/send/group?route=105&frameqq=3266363480&group=%s&key=key&newscontent=%s" % (
                group, msg)

            payload = {}
            headers = {
                'Content-Type': 'multipart/form-data'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)

            # url = "http://119.29.97.135:8888/sendgroupmsg"
            #
            # payload = '{"group":%d,"logonqq":3266363480,"msg":"%s"}' % (group, msg)
            # curr_stamp = int(time.time()) + 150
            #
            # message = "user1/sendgroupmsg" + hashlib.md5("root".encode()).hexdigest() + str(curr_stamp)
            #
            # message = hashlib.md5(message.encode('utf-8')).hexdigest()
            #
            # res = "user=user1;timestamp=" + str(curr_stamp) + ";signature=" + message
            #
            # headers = {
            #     'Content-Type': 'application/json',
            #     'Cookie': res
            # }
            #
            # response = requests.request("POST", url, headers=headers,timeout=30,
            #                             data=payload.replace('&nbsp;', '').replace('\xa0', ' ').encode(
            #                                 encoding='utf-8'))

            print(response.text)

        except Exception as e:
            print('send_group_msg', e)
        finally:
            requests.session().close()
            CommonInstance.App_IS_LOCKED = False
