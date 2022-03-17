# -*- coding: utf-8 -*-
import time
from typing import List

import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


class DaiLianMaMaCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.next_urls = []
        self.urls = [
            "http://m.dailianmama.com/v-3.0.9-zh_CN-/dlmm/index.w?language=zh_CN&skin=&ttt=random6833130&p3704878=pp1435623&t=1647424588903#!main"]
        for url in self.urls:
            self.result_map[url] = []
        self.file_location = 'hok_task_crawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'HokTaskCrawl start crawl..',
              browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath(
            '//div[contains(@data-bind,"event:{click:$model._callModelFn.bind($model, \'receiveOrder\')}")]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//span/text()')
            title = self.__trim_ele(title)

            area = sel.xpath('//p/text()')
            area = self.__trim_ele(area)

            end_time = sel.xpath('//h5/text()')
            end_time = self.__trim_ele(end_time)

            money = sel.xpath('//h4/text()')
            money = self.__trim_ele(money)

            key = title + area + end_time + money
            if CommonInstance.Redis_client.get(key) is not None:
                continue
            self.result_map[browser.current_url].append(HokTaskResult(title, money, end_time, area))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'HokTaskCrawl end crawl..',
              browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke start custom_send..', url)
            for data in self.result_map[url]:
                txt = '新的订单\n' \
                      '%s\n' \
                      '区服:%s\n' \
                      '价格:%s\n' \
                      '%s\n'\
                      'http://m.dailianmama.com/v-3.0.9-zh_CN-/dlmm/index.w?language=zh_CN&skin=&ttt=random6833130&p3704878=pp1435623&t=1647424588903#!main'% (data.title, data.area, data.money, data.end_time)
                time.sleep(1)
                CommonInstance.QQ_ROBOT.send_group_msg(group=461936572,
                                                       msg=[miraicle.Plain(txt)])
                key = data.title + data.area + data.end_time + data.money
                CommonInstance.Redis_client.set(key, '')

    def __trim_ele(self, ele: str):
        ele = ele[0] if len(ele) > 0 else ''
        return ele.replace('\n', '')


class HokTaskResult:
    def __init__(self, title, money, end_time, area):
        self.title = title
        self.money = money
        self.end_time = end_time
        self.area = area
