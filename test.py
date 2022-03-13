# -*- coding: utf-8 -*-
import crawl_mapping
from common_crawl import CommonCrawl
import miraicle

from crawl.hok_camp.hok_camp_crawl import HokCampCrawl
from middleware.rabbit_mq import init_middleware


# @miraicle.Mirai.receiver('GroupMessage')
# def hello_to_group(robot: miraicle.Mirai, msg: miraicle.GroupMessage):
#     if 'At:1208559252' in msg.text:
#         robot.send_group_msg(group=msg.group, msg='@我大哥干嘛@%s' % msg.sender_name)
#         return
#
#     if robot.qq in [3266363480]:
#         robot.send_group_msg(group=msg.group, msg=msg)
#     else:
#         pass
#
#
# @miraicle.Mirai.receiver('FriendMessage')
# def hello_to_friend(robot: miraicle.Mirai, msg: miraicle.FriendMessage):
#     robot.send_group_msg(group=msg.group, msg='咩~')


if __name__ == '__main__':
    qq = 3266363480  # 你登录的机器人 QQ 号
    verify_key = 'INITKEYurlPivoQ'  # 你在 setting.yml 中设置的 verifyKey
    port = 8060  # 你在 setting.yml 中设置的 port (http)

    bot = miraicle.Mirai(qq=qq, verify_key=verify_key, port=port)
    bot.run()
if __name__ == '__main__':
    init_middleware()
    crawl = HokCampCrawl()
    crawl.run(['f-nF3MbqfpLiE8HZ_BXw-AYKnlS9KxgWfJorw5AWvYDp5LaeV9Sgk5Nf2Gq7KqHXFxiUJczJaqrZv9jZr7_BCfWVvYuhd_0TaZpV2MGZlH2Lopl6wb5dge0PPJcBY7YoA_yf8f3wQzoBNMG2Z_z9nBQE9m91yY5F2vXlV9o05a6F5-XwtiZBuSakx_Z5P_kF'])
