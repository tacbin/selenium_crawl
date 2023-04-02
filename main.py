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
from crawl.big_company_jobs.meituan import MeiTuanCrawl
from crawl.big_company_jobs.oppo import OppoCrawl
from crawl.big_company_jobs.shangtang import ShangTangCrawler
from crawl.big_company_jobs.shen_xin_fu import ShenXinFuCrawl
from crawl.big_company_jobs.tencent import TencentCrawl
from crawl.big_company_jobs.tp_link import TpLinkCrawl
from crawl.big_company_jobs.vivo import VivoCrawl
from crawl.big_company_jobs.wangyi import WangYiCrawl
from crawl.big_company_jobs.weilai import WeiLaiCrawler
from crawl.big_company_jobs.weipai import WeiPaiCrawl
from crawl.big_company_jobs.xunlei import XunLeiCrawl
from crawl.big_company_jobs.zhaolian import ZhaoLianCrawler
from crawl.code_task.wei_ke_crawl import WeiKeCrawl
from crawl.code_task.zhu_ba_jie_crawl import ZhuBaJieCrawl
from crawl.english.youtube_music import YoutubeMusicCrawler
from middleware.init_middleware import init_middleware


def empty_run():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'empty running..')


# 若debug报错，启动时设置下值
# PYDEVD_USE_CYTHON=NO
# PYDEVD_USE_FRAME_EVAL=NO
if __name__ == '__main__':
    init_middleware()

    # mq_thread = MqThreadControl(1, 'mq thread')
    # mq_thread.start()

    # 创建后台执行的 schedulers
    # ZhuBaJieCrawl(), WeiKeCrawl()禁止爬
    while True:
        tasks = [BeiKeCrawl(), CsBeiKeCrawl(), ByteDanceCrawl(), AlibabaCrawl(),
                 BaiDuCrawl(), DaJiangCrawl(), FuTuCrawl(), XunLeiCrawl(), TencentCrawl(), OppoCrawl(), VivoCrawl(),
                 HuaWeiCrawl(), KuaiShouCrawl(), ShangTangCrawler(), TpLinkCrawl(), WeiLaiCrawler(), ZhaoLianCrawler()
            , MeiTuanCrawl(), WangYiCrawl(), WeiPaiCrawl(), ShenXinFuCrawl()]
        # tasks = [YoutubeMusicCrawler()]
        minutes = 60 * 2
        for task in tasks:
            task.run()
            time.sleep(60 * minutes / len(tasks))
