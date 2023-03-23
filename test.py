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

    msg = """【阿里巴巴招聘】岗位名称：达摩院-OCR和文档理解算法专家-北京/杭州地点：北京 / 杭州发布时间:更新于 
    2023-03-23链接://talent.alibaba.com/off-campus/position-detail?positionId=937509&track_id
    =SSP1679533762732uwnAZlKLLL5967 """
    group = 461936572
    url = "http://119.29.97.135:8888/send/group?route=105&frameqq=3266363480&group=%s&key=key&newscontent=%s" % (
        group, msg.replace('&nbsp;', '').replace('\xa0', ' '))
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send..',
          group, url)
    payload = {}
    headers = {
        'Content-Type': 'multipart/form-data',
        # "Accept-Charset": "utf-8",
        # "Accept-Charsets": "gbk",
        # "url-jsonurl-json": "true",
        # "Accept-Charsettype": "true"
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
