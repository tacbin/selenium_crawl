# -*- coding: utf-8 -*-
import multiprocessing
import threading
import json
import time

import miraicle

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot


class QQRobotThreadControl(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        qq = 3266363480  # 你登录的机器人 QQ 号
        verify_key = 'INITKEYurlPivoQ'  # 你在 setting.yml 中设置的 verifyKey
        port = 8080  # 你在 setting.yml 中设置的 port (http)
        CommonInstance.QQ_ROBOT = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
        CommonInstance.QQ_ROBOT.base_url = CommonInstance.QQ_ROBOT.base_url.replace('localhost', '119.29.97.135')
        CommonInstance.QQ_ROBOT.run()


@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(robot: miraicle.Mirai, msg: miraicle.GroupMessage):
    if 'At:1208559252' in msg.text or 'At:2840498397' in msg.text or 'At:52110919' in msg.text:
        QQRobot.send_group_msg(group=msg.group, msg=[miraicle.Plain('@我大哥干嘛'),
                                                     miraicle.At(msg.sender)])

        return
    if msg.at_me():
        QQRobot.send_group_msg(group=msg.group, msg=[miraicle.Plain('@我干嘛'),
                                                     miraicle.At(msg.sender),
                                                     miraicle.Face.from_name('汪汪')])
    if '呼叫小羊' in msg.plain:
        QQRobot.send_group_msg(group=msg.group, msg=[miraicle.Plain('大哥我来了~'),
                                                     miraicle.At(msg.sender),
                                                     miraicle.Face.from_name('悠闲')])

    if msg.group in [461936572]:
        robot.send_group_msg(group=msg.group, msg=msg)
    else:
        pass


@miraicle.Mirai.receiver('FriendMessage')
def hello_to_friend(robot: miraicle.Mirai, msg: miraicle.FriendMessage):
    robot.send_friend_msg(qq=msg.sender, msg='咩~')


@miraicle.scheduled_job(miraicle.Scheduler.every(1).day.at('8:40'))
def morning(bot: miraicle.Mirai):
    bot.send_group_msg(group=461936572, msg='早上好')
