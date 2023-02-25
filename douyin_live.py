# -*- coding: utf-8 -*-
from crawl.douyin.douyin_live_show import DouYinLiveCrawl
from middleware.init_middleware import init_middleware

if __name__ == '__main__':
    init_middleware()
    crawl = DouYinLiveCrawl('https://live.douyin.com/304908057646')
    crawl.run()