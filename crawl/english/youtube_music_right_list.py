# -*- coding: utf-8 -*-
import os
import threading
import time

import eyed3
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import Week, FuDuJiGroup
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from open_lib import youtube_dl
from utils.download_util import DownloadUtil
from utils.utils import get_current_time, safeFilename


class YoutubeMusicRightListCrawler(CommonCrawl):
    def __init__(self, url, title, jump=False):
        super().__init__()
        self.sub_dir = time.strftime('%Y-%m-%d', time.localtime())
        self.result_map = {}
        if not jump:
            last_time = CommonInstance.Redis_client.get('YoutubeMusicRightListCrawler')
            if last_time is None:
                last_time = get_current_time()
            else:
                last_time = int(last_time)
            if get_current_time() - Week < last_time:
                self.is_run = False
        self.show_head = True
        self.url = url
        self.title = title

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            self.url]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'YoutubeMusicRightListCrawler  '
        self.is_save_img = False
        self.mode = 1
        # self.sub_dir = '%s(%s)' % (self.title, self.sub_dir)
        # new_dir = 'E:/python-workspace/selenium_crawl/files/%s' % self.sub_dir
        # if not os.path.exists(new_dir):
        #     print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), new_dir, '创建目录,')
        #     os.makedirs(new_dir)
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler   start crawl..',
              browser.current_url)
        time.sleep(60)
        curr_url = browser.current_url
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'after sleep current_url:',curr_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//ytd-playlist-panel-video-renderer[@class='style-scope ytd-playlist-panel-renderer']")
        for task in tasks:
            try:
                sel = etree.HTML(etree.tostring(task, method='html'))

                url = sel.xpath("//ytd-playlist-panel-video-renderer//a/@href")
                if len(url) == 0:
                    continue
                url = url[0] if len(url) > 0 else ''
                url = url.strip()
                url = 'https://www.youtube.com' + url.replace('\n', '')
                print(url, ' end')
                self.result_map[curr_url].append(TaskResult(url))
            except:
                pass
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler   end crawl..',
              curr_url)

    def custom_send(self):
        i = 0
        threads = []
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                  'YoutubeMusicRightListCrawler   start custom_send..',
                  url)
            for data in self.result_map[url]:
                i += 1
                try:
                    thread = threadControl(data.url, i, self.title)
                    thread.start()
                    threads.append(thread)
                    # self.download_audio(data.url, i)
                except Exception as e:
                    print("YoutubeMusicRightListCrawler err:", e)
            for t in threads:
                t.join()
        CommonInstance.Redis_client.set('YoutubeMusicRightListCrawler', get_current_time())
        QQRobot.send_group_msg(FuDuJiGroup, ["youtube music 更新完毕"])
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'YoutubeMusicRightListCrawler  ending..')


class TaskResult:
    def __init__(self, url):
        self.type = 'youtube_music_top_50'
        self.url = url


class threadControl(threading.Thread):
    def __init__(self, url, i, sub_dir):
        super().__init__()
        self.url = url
        self.i = i
        self.sub_dir = sub_dir

    def run(self):
        DownloadUtil.download_audio(self.url, self.i,self.sub_dir)