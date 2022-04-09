# -*- coding: utf-8 -*-
import random
import time
from typing import List

from common.common_instantce import CommonInstance


class QQRobot:
    @staticmethod
    def send_group_msg(group: int, msg: List):
        pass
        # try:
        #     while CommonInstance.App_IS_LOCKED:
        #         time.sleep(random.randint(5, 15))
        #     CommonInstance.App_IS_LOCKED = True
        #     time.sleep(random.randint(1, 3))
        #     CommonInstance.QQ_ROBOT.send_group_msg(group=group,
        #                                            msg=msg)
        # except Exception as e:
        #     print('send_group_msg', e)
        # finally:
        #     CommonInstance.App_IS_LOCKED = False
