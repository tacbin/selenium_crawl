# -*- coding: utf-8 -*-
import crawl_mapping
from common_crawl import CommonCrawl

if __name__ == '__main__':
    crawl = crawl_mapping.crawl_factory("beike")
    if isinstance(crawl, CommonCrawl):
        crawl.run()
    else:
        print(crawl, 'does not implement CommonCrawl')
