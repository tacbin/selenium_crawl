# -*- coding: utf-8 -*-
import os
import sys

from crawl.english.youtube_music_right_list import YoutubeMusicRightListCrawler
from utils.download_util import DownloadUtil
from utils.utils import get_current_time

os.chdir('E:\python-workspace\selenium_crawl')
from middleware.init_middleware import init_middleware


def download_single_audio(url, i):
    DownloadUtil.download_audio(url, 999 + i)


def download_collection(url, title):
    init_middleware()
    tasks = [YoutubeMusicRightListCrawler(url, title, True)]
    for task in tasks:
        task.run()


# 黄明志推荐歌单    url = 'https://www.youtube.com/watch?v=jxA4xQbDcyE&list=RDjxA4xQbDcyE&start_radio=1&rv=jxA4xQbDcyE&t=1'
# 李圣杰推荐歌单 https://www.youtube.com/watch?v=7NIsBeVRAgk&list=RDEM196XDaIpRfMfFXqcWmH8RA&start_radio=1&rv=a1T2FVLP29M
# 五月天合辑 https://www.youtube.com/watch?v=V9sWPHGbESM&list=RDV9sWPHGbESM&start_radio=1&rv=V9sWPHGbESM&t=8
if __name__ == '__main__':
    # download_collection(
    #     'https://www.youtube.com/watch?v=zPeMFCDPgKE&list=RDQMUdz7ww5gH38&index=3', '好听的老歌')
    # download_single_audio('https://www.youtube.com/watch?v=vEajwiVHeYg',get_current_time())

    download_single_audio('https://www.youtube.com/watch?v=nBaYg4U8khA&ab_channel=%E6%B4%97%E8%84%91%E6%8A%96%E9%9F%B3%E6%AD%8C%E6%9B%B2',get_current_time())
