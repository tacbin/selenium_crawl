# -*- coding: utf-8 -*-
# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.

import crawl_mapping
from common_crawl import CommonCrawl

if __name__ == '__main__':
    args = ['运营总监', '技术总监', 'CTO', 'CEO', 'AI', '图像识别', '神经网络', '创业']
    crawl = crawl_mapping.obj_mapping['boss']
    if isinstance(crawl, CommonCrawl):
        crawl.run(args)
    else:
        print(crawl, 'does not implement CommonCrawl')
