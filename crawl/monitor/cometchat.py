# -*- coding: utf-8 -*-
import time
from typing import List
import re

import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class CometchatCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.next_urls = []
        self.urls = ["https://www.cometchat.com/blog"]
        for url in self.urls:
            self.result_map[url] = []
        self.file_location = 'Cometchat'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Cometchat parse start crawl..',
              browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        cards = selector.xpath(
            "//div[@role='listitem']")
        for card in cards:
            sel = etree.HTML(etree.tostring(card, method='html'))
            url = sel.xpath(
                "//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = "https://www.cometchat.com" + url

            date = sel.xpath('//div[@class="date-blog"]/text()')
            date = date[0] if len(date) > 0 else ''
            date = date.replace('\n', '')
            date = date.replace(' ', '')
            title = sel.xpath("//p[@class='text-gray text-medium']")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')
            if CommonInstance.Redis_client.get(url) is not None:
                continue

            self.result_map[browser.current_url].append(CometchatResult(title, url, date))

        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Cometchat parse end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Cometchat start custom_send..', url)
            for data in self.result_map[url]:
                txt = '【Cometchat】发文章啦\n' \
                      '标题:%s\n' \
                      '时间:%s\n' \
                      '链接:%s' % (data.title, data.date, data.url)
                QQRobot.send_group_msg(569108046, [miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')

    def get_next_urls(self, browser: WebDriver) -> List[str]:
        return self.next_urls


class CometchatResult:
    def __init__(self, title, url, date):
        self.title = title
        self.url = url
        self.date = date
