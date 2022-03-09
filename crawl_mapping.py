# -*- coding: utf-8 -*-
from common_crawl import CommonCrawl
from crawl.boss.boss_crawl import BossCrawl
from crawl.hok.hok_crwal import HokCrawl


def crawl_factory(crawl: str) -> CommonCrawl:
    if crawl == 'boss':
        return BossCrawl()
    elif crawl == "hok":
        return HokCrawl()
    else:
        print(crawl, 'does not implement CommonCrawl')
