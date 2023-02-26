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


class FuTuCrawl (CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://app.mokahr.com/apply/futu5/1698#/jobs?zhineng=14314","https://app.mokahr.com/apply/futu5/1698#/jobs?zhineng=14315","https://app.mokahr.com/apply/futu5/1698#/jobs?zhineng=14320"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'FuTuCrawl  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FuTuCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="link-2tgd22te-3"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div[@class="title-20V7ljm-Id"]/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath('//div[@class="status-2vTS8JvF_D"]//text()')
            cate = cate[0] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            place = sel.xpath('//div[@class="locations-32aEgVWFz_"]//text()')
            place = place[0] if len(place) > 0 else ''
            place = place.replace('\n', '')


            url = sel.xpath('//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = 'https://app.mokahr.com/apply/futu5/1698' + url.replace('\n', '')

            self.result_map[browser.current_url].append(TaskResult(title, place, cate, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FuTuCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FuTuCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '【富途招聘】\n' \
                      '岗位名称：%s\n' \
                      '类目:%s\n' \
                      '地点：%s\n' \
                      '链接:%s' % (data.title, data.cate, data.place, data.url)
                QQRobot.send_group_msg(JobGroupConstant, [miraicle.Plain(txt)])
                CommonInstance.Redis_client.set(data.url, '')


class TaskResult:
    def __init__(self, title, place, cate, url):
        self.title = title
        self.place = place
        self.cate = cate
        self.url = url
