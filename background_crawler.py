# -*- coding: utf-8 -*-
import os
import sys

from crawl.english.youtube_music_right_list import YoutubeMusicRightListCrawler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\selenium_crawl'
print('\n', BASE_DIR)
sys.path.append(BASE_DIR)
from middleware.init_middleware import init_middleware

# 黄明志推荐歌单    url = 'https://www.youtube.com/watch?v=jxA4xQbDcyE&list=RDjxA4xQbDcyE&start_radio=1&rv=jxA4xQbDcyE&t=1'
# 李圣杰推荐歌单 https://www.youtube.com/watch?v=7NIsBeVRAgk&list=RDEM196XDaIpRfMfFXqcWmH8RA&start_radio=1&rv=a1T2FVLP29M
if __name__ == '__main__':
    init_middleware()
    url = 'https://www.youtube.com/watch?v=7NIsBeVRAgk&list=RDEM196XDaIpRfMfFXqcWmH8RA&start_radio=1&rv=a1T2FVLP29M'
    title = '李圣杰推荐歌单'
    tasks = [YoutubeMusicRightListCrawler(url, title, True)]
    for task in tasks:
        task.run()
