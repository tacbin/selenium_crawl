# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver

from common_crawl import CommonCrawl
import time
import json

from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class GetPcSoftsCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.getpcsofts.net/"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'GetPcSoftsCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GetPcSoftsCrawlstart crawl..',
              browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//article[contains(@class,'group')]")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//article[contains(@class,'group ')]//h2//a/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '').strip()

            date = sel.xpath("//article[contains(@class,'group ')]//time[contains(@class,'published')]/text()")
            date = date[0] if len(date) > 0 else ''
            date = date.replace('\n', '').strip()

            desc = sel.xpath("//article[contains(@class,'group ')]//div[contains(@class,'entry')]//p/text()")
            desc = desc[0] if len(desc) > 0 else ''
            desc = desc.replace('\n', '').strip()

            url = sel.xpath("//article[contains(@class,'group ')]//h2//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')

            self.result_map[browser.current_url].append(TaskResult(title, date, desc, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GetPcSoftsCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GetPcSoftsCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【PC破解软件】\n\n' \
                      '标题：%s\n\n' \
                      '日期:%s\n\n' \
                      '描述:%s\n\n' \
                      '链接:%s' % (data.title, data.date, data.desc, data.url)

                QQRobot.send_blogs([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, date, desc, url):
        self.title = title
        self.date = date
        self.desc = desc
        self.url = url
