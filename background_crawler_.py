# -*- coding: utf-8 -*-

from crawl.english.youtube_music import YoutubeMusicCrawler

if __name__ == '__main__':
    tasks = [YoutubeMusicCrawler()]
    for r in tasks:
        r.run()
