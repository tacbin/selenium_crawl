# -*- coding: utf-8 -*-
import time

import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


class ZhuBaJieCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://task.zbj.com/hall/list/h1", "https://task.zbj.com/hall/list/h7",
                     "https://task.zbj.com/hall/list/h9"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'zhu_ba_jie_crawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'zhu ba jie start crawl..', browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="result-search-item"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div//h4/@title')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            detail = sel.xpath("//div[@class='pub-desc text-line-overflow-two']/text()")
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')

            money = sel.xpath('//div[@class="pub-handles"]//span/text()')
            money = money[0] if len(money) > 0 else ''
            money = money.replace('\n', '')

            url = sel.xpath('//h4//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = url.replace('//', '')

            self.result_map[browser.current_url].append(ZhuBaJieTaskResult(title, detail, money, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'zhu ba jie end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'zhu ba jie start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '商机来啦\n' \
                      '【%s】\n' \
                      '详情:%s\n' \
                      '价格:%s\n' \
                      '链接:%s' % (data.title, data.detail, data.money, data.url)
                time.sleep(1)
                CommonInstance.QQ_ROBOT.send_group_msg(group=461936572,
                                                       msg=[miraicle.Plain(txt)])
                time.sleep(1)
                CommonInstance.QQ_ROBOT.send_group_msg(group=963961013,
                                                       msg=[miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')


class ZhuBaJieTaskResult:
    def __init__(self, title, detail, money, url):
        self.title = title
        self.detail = detail
        self.money = money
        self.url = url
