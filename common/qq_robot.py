# -*- coding: utf-8 -*-
import time
from typing import List

from common.common_instantce import CommonInstance


class QQRobot:
    @staticmethod
    def send_group_msg(group: int, msg: List):
        lock_name = 'send_group_lock'
        try:
            while CommonInstance.Redis_client.get(lock_name) is not None:
                time.sleep(5)
            CommonInstance.Redis_client.set(lock_name, 'locked', ex=10)
            time.sleep(1)
            CommonInstance.QQ_ROBOT.send_group_msg(group=group,
                                                   msg=msg)
        except Exception as e:
            print('send_group_msg', e)
        finally:
            CommonInstance.Redis_client.delete(lock_name)
