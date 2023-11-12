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


class FsiLanguageCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.fsi-language-courses.org/"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'FsiLanguageCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FsiLanguageCrawlstart crawl..',
              browser.current_url)
        time.sleep(5)

        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[contains(@class,'grid')]//div[contains(@class,'w-full')]")

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n fsi language 解析失败!无解析信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//div[contains(@class,'border-b')]//a//span/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '').strip()

            desc = sel.xpath("//div[contains(@class,'px-10')]/text()")
            desc = desc[0] if len(desc) > 0 else ''
            desc = desc.replace('\n', '').strip()

            if len(desc) == 0:
                continue

            date = ''

            url = sel.xpath("//div[contains(@class,'border-b')]//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = 'https://www.fsi-language-courses.org' + url

            self.result_map[browser.current_url].append(TaskResult(title, date, desc, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FsiLanguageCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'FsiLanguageCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【fsi-blog】\n\n' \
                      '标题：%s\n\n' \
                      '简介:%s\n\n' \
                      '链接:%s' % (data.title, data.desc, data.url)

                QQRobot.send_blogs([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, date, desc, url):
        self.title = title
        self.date = date
        self.desc = desc
        self.url = url
