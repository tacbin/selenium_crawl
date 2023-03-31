# -*- coding: utf-8 -*-
import hashlib
import time

import crawl_mapping
from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl
import miraicle

from crawl.beike.beike_crawl import BeiKeCrawl
from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from crawl.confluence.confluence import ConfluenceCrawl
from crawl.douyin.douyin_live_msg import DouYinMsgLiveCrawl
from crawl.douyin.douyin_live_show import DouYinLiveCrawl
from crawl.hok_task.dai_lian_ma_ma_crawl import DaiLianMaMaCrawl
from middleware.init_middleware import init_middleware
from threads.qq_robot_thread import QQRobotThreadControl

if __name__ == '__main__':
    wl = DouYinMsgLiveCrawl('https://live.douyin.com/574902600741')
    wl.run()
    # import requests
    #
    # url = "http://localhost:8080/live"
    # payload = "{\"message\":\"%s\",\"appId\":\"xaa\",\"token\":\"fff\",\"timestamp\":1111}" % "hello"
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)