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
    import requests

    url = "http://119.29.97.135:8888/send/group"

    payload = {'route': '105',
               'frameqq': '3266363480',
               'group': '858288116',
               'key': 'key',
               'newscontent': '脚后跟 '}

    headers = {
        'Content-Type': 'multipart/form-data',
        'Accept-Charset': 'utf-8',
        'Accept-Charsets': 'gbk',
        'url-jsonurl-json': 'true',
        'Accept-Charsettype': 'true',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


