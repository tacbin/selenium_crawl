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


class ProductHuntCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.producthunt.com/"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'ProductHuntCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ProductHuntCrawlstart crawl..',
              browser.current_url)
        time.sleep(15)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[contains(@class,'px-mobile-1')]")

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n ProductHunt解析失败!无解析信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//a[@class='styles_title__HzPeb']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '').strip()

            if len(title) == 0:
                continue

            date = ''

            desc = sel.xpath("//a[@class='styles_tagline__Dwvza']/text()")
            desc = ''.join(desc)
            desc = desc.replace('\n', '').strip()

            url = sel.xpath("//a[@class='styles_title__HzPeb']/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = 'https://www.producthunt.com' + url
            self.result_map[browser.current_url].append(TaskResult(title, date, desc, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ProductHuntCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ProductHuntCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【Product Hunt】\n\n' \
                      '标题：%s\n\n' \
                      '描述:%s\n\n' \
                      '链接:%s' % (data.title, data.desc, data.url)

                QQRobot.send_to_idea([txt])
                QQRobot.send_to_idea_xiaowo([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, date, desc, url):
        self.title = title
        self.date = date
        self.desc = desc
        self.url = url
