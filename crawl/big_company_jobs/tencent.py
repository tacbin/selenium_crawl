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


class TencentCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://careers.tencent.com/search.html?pcid=40001",
                     "https://careers.tencent.com/search.html?pcid=40006",
                     "https://careers.tencent.com/search.html?query=ot_40003001,ot_40003002,ot_40003003"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'TencentCrawl  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="recruit-list"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//h4[@class="recruit-title"]/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath('//p[@class="recruit-tips"]//text()')
            cate = cate[0] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            detail = sel.xpath('//p[@class="recruit-text"]//text()')
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')

            url = 'https://careers.tencent.com/search.html?pcid=40001&' + title + cate + time.strftime('%Y-%m-%d')

            self.result_map[browser.current_url].append(TaskResult(title, detail, cate, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '【腾讯招聘】\n' \
                      '岗位名称：%s\n' \
                      '类目:%s\n' \
                      '详情：%s\n' \
                      '链接:%s' % (data.title, data.cate, data.detail, data.url.split("&")[0])
                QQRobot.send_group_msg(JobGroupConstant, [miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   end custom_send..', url)


class TaskResult:
    def __init__(self, title, detail, cate, url):
        self.title = title
        self.detail = detail
        self.cate = cate
        self.url = url
