# -*- coding: utf-8 -*-
import time

import miraicle
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class XieChengCrawl (CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://flights.ctrip.com/online/list/round-szx-krl?depdate=2023-04-27_2023-05-05&cabin=y_s_c_f&adult=1&child=0&infant=0&source_module=recommend_card"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'XieChengCrawl  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        list_cookies = self.load_cookie(browser, './xiecheng.json')
        browser.delete_all_cookies()
        for cookie in list_cookies:
            browser.add_cookie(cookie_dict=cookie)
        browser.refresh()
        time.sleep(120)
        self.save_cookie(browser, './xiecheng.json')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'XieChengCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="flight-box"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            duration = sel.xpath('//span[@class="transfer-duration"]//text()')
            duration = duration[0] if len(duration) > 0 else ''
            duration = duration.replace('\n', '')

            price = sel.xpath('//span[@class="price"]//text()')
            price = price[0] if len(price) > 0 else ''
            price = price.replace('\n', '')

            self.result_map[browser.current_url].append(TaskResult(duration, price))
        self.save_cookie(browser, './xiecheng.json')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'XieChengCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'XieChengCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '【携程机票】\n' \
                      '中转时长：%s\n' \
                      '价格:%s\n'  % (data.duration, data.price)
                QQRobot.send_group_msg(JobGroupConstant, [miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')


class TaskResult:
    def __init__(self, duration, price):
        self.duration = duration
        self.price = price
