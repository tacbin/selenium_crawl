# -*- coding: utf-8 -*-
import time

from crawl.beike.beike_crawl import BeiKeCrawl
from crawl.beike.cs_beike_crawl import CsBeiKeCrawl
from crawl.big_company_jobs.alibaba import AlibabaCrawl
from crawl.big_company_jobs.baidu import BaiDuCrawl
from crawl.big_company_jobs.bytedance import ByteDanceCrawl
from crawl.big_company_jobs.dajiang import DaJiangCrawl
from crawl.big_company_jobs.futu import FuTuCrawl
from crawl.big_company_jobs.huawei import HuaWeiCrawl
from crawl.big_company_jobs.kuaishou import KuaiShouCrawl
from crawl.big_company_jobs.oppo import OppoCrawl
from crawl.big_company_jobs.shangtang import ShangTangCrawler
from crawl.big_company_jobs.tencent import TencentCrawl
from crawl.big_company_jobs.tp_link import TpLinkCrawl
from crawl.big_company_jobs.vivo import VivoCrawl
from crawl.big_company_jobs.weilai import WeiLaiCrawler
from crawl.big_company_jobs.xunlei import XunLeiCrawl
from crawl.big_company_jobs.zhaolian import ZhaoLianCrawler
from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from middleware.init_middleware import init_middleware
from threads.mq_thread import MqThreadControl


def empty_run():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'empty running..')


# 若debug报错，启动时设置下值
# PYDEVD_USE_CYTHON=NO
# PYDEVD_USE_FRAME_EVAL=NO
if __name__ == '__main__':
    init_middleware()

    mq_thread = MqThreadControl(1, 'mq thread')
    mq_thread.start()

    # 创建后台执行的 schedulers
    tasks = [ZhuBaJieCrawl(), WeiKeCrawl(), BeiKeCrawl(), CsBeiKeCrawl(), ByteDanceCrawl(), AlibabaCrawl(),
             BaiDuCrawl(), DaJiangCrawl(), FuTuCrawl(), XunLeiCrawl(), TencentCrawl(), OppoCrawl(), VivoCrawl(),
             HuaWeiCrawl(), KuaiShouCrawl(), ShangTangCrawler(), TpLinkCrawl(), WeiLaiCrawler(), ZhaoLianCrawler()]
    # tasks = [TencentCrawl()]
    while True:
        for task in tasks:
            task.run()
            time.sleep(60 * 10 / len(tasks))
