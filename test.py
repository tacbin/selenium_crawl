# -*- coding: utf-8 -*-
import crawl_mapping
from common_crawl import CommonCrawl
from crawl.hok_camp.hok_camp_crawl import HokCampCrawl
from middleware.rabbit_mq import init_middleware

if __name__ == '__main__':
    init_middleware()
    crawl = HokCampCrawl()
    crawl.run(['f-nF3MbqfpLiE8HZ_BXw-AYKnlS9KxgWfJorw5AWvYDp5LaeV9Sgk5Nf2Gq7KqHXFxiUJczJaqrZv9jZr7_BCfWVvYuhd_0TaZpV2MGZlH2Lopl6wb5dge0PPJcBY7YoA_yf8f3wQzoBNMG2Z_z9nBQE9m91yY5F2vXlV9o05a6F5-XwtiZBuSakx_Z5P_kF'])
