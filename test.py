# -*- coding: utf-8 -*-
import crawl_mapping
from common_crawl import CommonCrawl
import miraicle

from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from middleware.init_middleware import init_middleware
from threads.qq_robot_thread import QQRobotThreadControl

if __name__ == '__main__':
    init_middleware()
    qq_thread = QQRobotThreadControl(2, 'qq thread')
    qq_thread.start()
    crawl = WeiKeCrawl()
    crawl.run()
