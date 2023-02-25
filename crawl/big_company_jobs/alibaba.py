# -*- coding: utf-8 -*-
import time

import miraicle
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class AlibabaCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://talent.alibaba.com/off-campus/position-list?lang=zh"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'AlibabaCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'AlibabaCrawl start crawl..', browser.current_url)
        eles = browser.find_elements(By.XPATH,
                                     '//div[@aria-label="技术类"]//span[contains(@class,"next-tree-switcher next-noline")]')
        eles[0].click()
        eles = browser.find_elements(By.XPATH, '//input[@aria-label="开发"]')
        eles[0].click()
        eles = browser.find_elements(By.XPATH, '//input[@aria-label="深圳"]')
        eles[0].click()
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="_2AOmjKmlEtuR_KEoehWYcN"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//div[@class='_1RRlPtjyYmeDGCWt9lrk2P _3vj2eS7k7Mwpko5_6OSRu2']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            update_time = sel.xpath("//div[@class='_3Jn5Z6PZA5H7Auzy0xlXu2']/text()")
            update_time = update_time[0] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            url = "https://talent.alibaba.com/off-campus/position-list?lang=zh&"+title+update_time

            self.result_map[browser.current_url].append(TaskResult(title, update_time, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'AlibabaCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'AlibabaCrawl start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '阿里巴巴\n' \
                      '【%s】\n' \
                      '发布时间:%s\n' \
                      '链接:%s' % (data.title, data.update_time, data.url.split("&")[0])
                QQRobot.send_group_msg(461936572, [miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')


class TaskResult:
    def __init__(self, title, update_time, url):
        self.title = title
        self.update_time = update_time
        self.url = url
