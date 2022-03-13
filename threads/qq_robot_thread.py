# -*- coding: utf-8 -*-
import multiprocessing
import threading
import time

import miraicle


class QQRobotThreadControl(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        proc = multiprocessing.Process(target=run_http, args=())
        proc.start()
        while True:
            time.sleep(300)
            proc.terminate()
            proc = multiprocessing.Process(target=run_http, args=())
            proc.start()


def run_http():
    qq = 3266363480  # 你登录的机器人 QQ 号
    verify_key = 'INITKEYurlPivoQ'  # 你在 setting.yml 中设置的 verifyKey
    port = 8080  # 你在 setting.yml 中设置的 port (http)
    mirai = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
    mirai.base_url = mirai.base_url.replace('localhost', '119.29.97.135')
    mirai.run()


@miraicle.Mirai.receiver('GroupMessage')
def hello_to_group(robot: miraicle.Mirai, msg: miraicle.GroupMessage):
    if 'At:1208559252' in msg.text or 'At:2840498397' in msg.text:
        robot.send_group_msg(group=msg.group, msg=[miraicle.Plain('@我大哥干嘛'),
                                                   miraicle.At(msg.sender)])
        return
    if msg.at_me():
        robot.send_group_msg(group=msg.group, msg=[miraicle.Plain('@我干嘛'),
                                                   miraicle.At(msg.sender),
                                                   miraicle.Face.from_name('汪汪')])

    if msg.group in [461936572]:
        robot.send_group_msg(group=msg.group, msg=msg)
    else:
        pass


@miraicle.Mirai.receiver('FriendMessage')
def hello_to_friend(robot: miraicle.Mirai, msg: miraicle.FriendMessage):
    robot.send_group_msg(group=msg.sender, msg='咩~')
