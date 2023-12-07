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
    #     'https://www.youtube.com/watch?v=tkZVFJCpRqA&list=RDEMzM_DSOih_4ee94yJwG-Lyg&index=3', '凤凰传奇')
    # download_single_audio('https://www.youtube.com/watch?v=vEajwiVHeYg',get_current_time())
    download_single_audio('https://youtu.be/Vf6EDkIuviA',get_current_time())
    download_single_audio('https://youtu.be/CMGsgQ2Jq_w',get_current_time())
    download_single_audio('https://youtu.be/7_7slY0fXNU',get_current_time())
    download_single_audio('https://youtu.be/pTZWvGIr8PE',get_current_time())