# -*- coding: utf-8 -*-
from common_crawl import CommonCrawl
from crawl.beike.beike_crawl import BeiKeCrawl
from crawl.boss.boss_crawl import BossCrawl
from crawl.hok.hok_crwal import HokCrawl


def crawl_factory(crawl: str) -> CommonCrawl:
    if crawl == 'boss':
        return BossCrawl()
    elif crawl == "hok":
        return HokCrawl()
    elif crawl == "beike":
        return BeiKeCrawl()
    else:
        print(crawl, 'does not implement CommonCrawl')
