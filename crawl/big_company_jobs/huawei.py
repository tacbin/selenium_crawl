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


class HuaWeiCrawl (CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://career.huawei.com/reccampportal/portal5/social-recruitment.html"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'HuaWeiCrawl  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'HuaWeiCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//li[@class="border-top"]')

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n 华为招聘解析失败!无岗位信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//h6/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')



            place = sel.xpath('//p//text()')
            place = ','.join(place)
            place = place.replace('\n', '')

            cate = ''

            url = sel.xpath('//a/@href')
            url = ''.join(url)
            url = 'https://career.huawei.com/reccampportal/portal5/' + url.replace('\n', '')

            self.result_map[browser.current_url].append(TaskResult(title, place, cate, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'HuaWeiCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'HuaWeiCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【华为招聘】\n\n' \
                      '岗位名称：%s\n\n' \
                      '地点：%s\n\n' \
                      '链接:%s' % (data.title, data.place, data.url)

                QQRobot.send_group_msg(JobGroupConstant, [txt])
                QQRobot.send_company_msg_xiaowo(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, place, cate, url):
        self.company = '华为招聘'
        self.title = title
        self.place = place
        self.cate = cate
        self.url = url
