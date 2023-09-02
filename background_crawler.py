# -*- coding: utf-8 -*-
import os
import sys

from crawl.english.youtube_music_right_list import YoutubeMusicRightListCrawler

os.chdir('E:\python-workspace\selenium_crawl')
from middleware.init_middleware import init_middleware

# 黄明志推荐歌单    url = 'https://www.youtube.com/watch?v=jxA4xQbDcyE&list=RDjxA4xQbDcyE&start_radio=1&rv=jxA4xQbDcyE&t=1'
# 李圣杰推荐歌单 https://www.youtube.com/watch?v=7NIsBeVRAgk&list=RDEM196XDaIpRfMfFXqcWmH8RA&start_radio=1&rv=a1T2FVLP29M
if __name__ == '__main__':
    init_middleware()
    url = 'https://www.youtube.com/watch?v=V9sWPHGbESM&list=RDV9sWPHGbESM&start_radio=1&rv=V9sWPHGbESM&t=8'
    title = '五月天合辑'
    tasks = [YoutubeMusicRightListCrawler(url, title, True)]
    for task in tasks:
        task.run()
