# -*- coding: utf-8 -*-
import hashlib
import time

import crawl_mapping
from common_crawl import CommonCrawl
import miraicle

from crawl.beike.beike_crawl import BeiKeCrawl
from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from crawl.confluence.confluence import ConfluenceCrawl
from crawl.douyin.douyin_live_show import DouYinLiveCrawl
from crawl.hok_task.dai_lian_ma_ma_crawl import DaiLianMaMaCrawl
from middleware.init_middleware import init_middleware
from threads.qq_robot_thread import QQRobotThreadControl

if __name__ == '__main__':
    group = 858288116
    msg = "我复活了"

    import requests

    url = "http://119.29.97.135:8888/sendgroupmsg"

    payload = '{"group":%d,"logonqq":3266363480,"msg":"%s"}' % (group,msg)
    curr_stamp = int(time.time()) + 150

    message = "user1/sendgroupmsg" + hashlib.md5("root".encode()).hexdigest() + str(curr_stamp)

    message = hashlib.md5(message.encode('utf-8')).hexdigest()

    res = "user=user1;timestamp=" + str(curr_stamp) + ";signature=" + message

    headers = {
        'Content-Type': 'application/json',
        'Cookie': res
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    print(response.text)

    # import requests
    #
    # url = "http://119.29.97.135:8888/sendgroupmsg"
    #
    # payload = "{\"group\":858288116,\r\n\"logonqq\":3266363480,\r\n\"msg\":\"ffff\"}"
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Cookie': 'user=user1;timestamp=1678524193;signature=4d7ba933f6a708306ab9b460277b38e0'
    # }
    #
    # response = requests.request("POST", url, headers=headers, data=payload)
    #
    # print(response.text)

