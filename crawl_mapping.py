# -*- coding: utf-8 -*-
from crawl.boss.boss_crawl import BossCrawl
from crawl.hok.hok_crwal import HokCrawl

obj_mapping = {
    "boss": BossCrawl(),
    "hok": HokCrawl()
}
