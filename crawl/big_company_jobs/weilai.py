# -*- coding: utf-8 -*-
import json
import time


from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class WeiLaiCrawler (CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://www.nio.cn/careers/jobs"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'WeiLaiCrawler'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiLaiCrawler   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//li[@class="CareerListCN_CareerListItem__GvZqM CareerListCN_CareerListCurrentPage__nqqfD"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div[@class="CareerListCN_CareerListItemTitle__2fqQE"]/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath('//div[@class="CareerListCN_CareerListItemDepartment__IxrSA"]//span/text()')
            cate = cate[0] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            place = sel.xpath('//div[@class="CareerListCN_CareerListItemLocation__JaJsH"]/text()')
            place = place[0] if len(place) > 0 else ''
            place = place.replace('\n', '')

            update_time = sel.xpath('//div[@class="CareerListCN_CareerListItemOpenDate__vZ4g8"]/text()')
            update_time = update_time[0] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            url = sel.xpath('//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')

            self.result_map[browser.current_url].append(TaskResult(title, place, cate,update_time, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiLaiCrawler   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiLaiCrawler   start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【NIO蔚来招聘】\n' \
                      '岗位名称：%s\n' \
                      '类目:%s\n' \
                      '地点：%s\n' \
                      '发布时间：%s\n' \
                      '链接:%s' % (data.title, data.cate, data.place,data.update_time, data.url)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__,ensure_ascii=False)))
                except Exception as e:
                    print("mq err:",e)


class TaskResult:
    def __init__(self, title, place, cate,update_time, url):
        self.company = 'NIO蔚来招聘'
        self.title = title
        self.place = place
        self.cate = cate
        self.update_time = update_time
        self.url = url
