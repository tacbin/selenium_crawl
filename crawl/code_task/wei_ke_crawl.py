# -*- coding: utf-8 -*-
import time
from typing import List
import re

import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


class WeiKeCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = ["https://task.epwk.com/?o=7"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'wei_ke_crawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke parse start crawl..',
              browser.current_url)
        if browser.current_url in self.urls:
            self.__list_strategy(browser)
        else:
            self.__detail_strategy(browser)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke parse end crawl..', browser.current_url)

    def __list_strategy(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke list_strategy start crawl..',
              browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='content-lists']//div[contains(@class,'itemblock')]")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//a[@class="text_over"]/@title')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            url = sel.xpath('//a[@class="text_over"]/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            if CommonInstance.Redis_client.get(url) is not None:
                continue
            self.next_urls.append(url)

            money = sel.xpath('//span[@class="price"]/text()')
            money = money[0] if len(money) > 0 else ''
            money = money.replace('\n', '')
            self.result_map[browser.current_url].append(WeiKeTaskResult(title, url, money))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke list_strategy end crawl..',
              browser.current_url)

    def __detail_strategy(self, browser: WebDriver):
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        try:
            detail = etree.tostring(selector.xpath("//div[@class='task-info-content']")[0], encoding='utf-8',
                                    method='html')
            dr = re.compile(r'<[^>]+>', re.S)
            dd = dr.sub('', detail.decode('utf-8'))
            dd = dd.replace('\n', '')
            dd = dd.replace(' ', '')
            for url in self.urls:
                for item in self.result_map[url]:
                    if item.url == browser.current_url:
                        item.detail = dd
        except Exception as e:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'detail_strategy exception:', e)

    def custom_send(self):
        for url in self.result_map:
            time.sleep(1)
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke start custom_send..', url)
            for data in self.result_map[url]:
                txt = '商机来啦\n' \
                      '%s\n' \
                      '详情:%s\n' \
                      '价格:%s\n' \
                      '链接:%s' % (data.title, data.detail, data.money, data.url)
                CommonInstance.QQ_ROBOT.send_group_msg(group=461936572,
                                                       msg=[miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')

    def get_next_urls(self, browser: WebDriver) -> List[str]:
        return self.next_urls


class WeiKeTaskResult:
    def __init__(self, title, url, money):
        self.title = title
        self.url = url
        self.money = money
        self.detail = ''
