# -*- coding: utf-8 -*-
from apscheduler.schedulers.background import BackgroundScheduler

from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from middleware.init_middleware import init_middleware
from threads.mq_thread import MqThreadControl
from threads.qq_robot_thread import QQRobotThreadControl

if __name__ == '__main__':
    init_middleware()
    mq_thread = MqThreadControl(1, 'mq thread')
    mq_thread.start()

    qq_thread = QQRobotThreadControl(2, 'qq thread')
    qq_thread.start()

    # 创建后台执行的 schedulers
    scheduler = BackgroundScheduler()
    # 添加调度任务
    crawl = ZhuBaJieCrawl()
    scheduler.add_job(crawl.run, 'interval', seconds=1800)
    # 启动调度任务
    print('启动调度任务')
    scheduler.start()
