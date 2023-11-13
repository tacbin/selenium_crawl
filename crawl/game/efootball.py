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


class EfootballCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        # self.use_proxy = True


    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.konami.com/efootball/zh-cn/topic/news/list"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'EfootballCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'EfootballCrawlstart crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='news-list']//ul//li//a")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//h1[@class='title']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '').strip()

            date = sel.xpath("//p[@class='date']/text()")
            date = date[0] if len(date) > 0 else ''
            date = date.replace('\n', '').strip()

            url = sel.xpath("//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '').strip()
            url = 'https://www.konami.com' + url

            self.result_map[browser.current_url].append(TaskResult(title, date, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'EfootballCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'EfootballCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【%s】\n\n' \
                      '标题：%s\n\n' \
                      '发布时间:%s\n\n' \
                      '链接:%s' % (data.game, data.title, data.date, data.url)

                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, date, url):
        self.game = 'Efootball'
        self.title = title
        self.date = date
        self.url = url
