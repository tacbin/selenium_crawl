# -*- coding: utf-8 -*-
from common_crawl import CommonCrawl
import json
import platform
import threading
import time

import selenium
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance

from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class DouYinMsgLiveCrawl(CommonCrawl):
    def __init__(self, live_url):
        super().__init__()
        self.live_url = live_url
        self.result_map = {}
        self.show_head = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = [self.live_url]
        self.mode = 1
        self.file_location = 'dou_yin_live_crawl'
        self.is_save_img = False
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'start crawl..', browser.current_url)
        msg_dict = set()
        while True:
            try:
                time.sleep(10)
                page = browser.page_source
                etree = html.etree
                selector = etree.HTML(page)
                msgs = selector.xpath("//span[@class='webcast-chatroom___content-with-emoji-text']/text()")
                # for msg in msgs:
                msg = msgs[-1]
                msg = '#%s' % msg

                if msg in msg_dict:
                    continue
                print(msg)
                msg_dict.add(msg)
                try:
                    import requests
                    url = "http://localhost:8080/live"
                    payload = "{\"message\":\"%s\",\"appId\":\"xaa\",\"token\":\"fff\",\"timestamp\":1111}" % msg
                    headers = {
                        'Content-Type': 'application/json'
                    }
                    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))
                    print(response.text)
                except Exception as e:
                    print("req err:", e)
            except:
                pass
