# -*- coding: utf-8 -*-
import time

from apscheduler.schedulers.background import BackgroundScheduler

from crawl.beike.beike_crawl import BeiKeCrawl
from crawl.beike.cs_beike_crawl import CsBeiKeCrawl
from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from crawl.monitor.agora import AgoraCrawl
from crawl.monitor.cometchat import CometchatCrawl
from crawl.monitor.ms import MsCrawl
from middleware.init_middleware import init_middleware
from threads.mq_thread import MqThreadControl
from threads.qq_robot_thread import QQRobotThreadControl


def empty_run():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'empty running..')


if __name__ == '__main__':
    init_middleware()
    mq_thread = MqThreadControl(1, 'mq thread')
    mq_thread.start()

    qq_thread = QQRobotThreadControl(2, 'qq thread')
    qq_thread.start()

    # 创建后台执行的 schedulers
    scheduler = BackgroundScheduler()
    scheduler.add_job(empty_run, 'interval', seconds=300)
    # 添加调度任务
    ms = MsCrawl()
    scheduler.add_job(ms.run, 'interval', seconds=1)

    agora = AgoraCrawl()
    scheduler.add_job(agora.run, 'interval', seconds=1)

    cometchat = CometchatCrawl()
    scheduler.add_job(cometchat.run, 'interval', seconds=1)

    # 启动调度任务
    print('启动调度任务')
    scheduler.start()
