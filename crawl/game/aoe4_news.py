# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import time
import json

from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class Aoe4NewsCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://steamcommunity.com/app/1466860/allnews/"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'Aoe4NewsCrawl'
        self.is_save_img = False
        self.mode = 1
        self.use_proxy = True
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Aoe4NewsCrawlstart crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='apphub_CardContentMain']")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//div[@class='apphub_CardContentNewsTitle']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            date = sel.xpath("//div[@class='apphub_CardContentNewsDate']/text()")
            date = date[0] if len(date) > 0 else ''
            date = date.replace('\n', '')

            url = "https://steamcommunity.com/app/1466860/allnews/"

            self.result_map[browser.current_url].append(TaskResult(title, date, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Aoe4NewsCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Aoe4NewsCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【%s】\n' \
                      '标题：%s\n' \
                      '发布时间:%s\n' \
                      '链接:%s' % (data.game, data.title, data.date, data.url)

                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, date, url):
        self.game = '帝国时代4'
        self.title = title
        self.date = date
        self.url = url
