# -*- coding: utf-8 -*-
from crawl.english.bbc_news import BBCNewsCrawler
from crawl.english.youtube_music import YoutubeMusicCrawler
from middleware.init_middleware import init_middleware

if __name__ == '__main__':
    init_middleware()

    tasks = [YoutubeMusicCrawler()]
    for task in tasks:
        task.run()
