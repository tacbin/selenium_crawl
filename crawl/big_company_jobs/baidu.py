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
from middleware.rabbit_mq import get_rabbit_mq_channel


class BaiDuCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://talent.baidu.com/jobs/social-list?search="]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'BaiDuCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'BaiDuCrawl start crawl..', browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="post-item__D6QB-"]')
        eles = browser.find_elements(By.XPATH,
                                     "//div[@class='post-title-content__5QLz1']")
        i = 0
        if len(eles) != len(tasks):
            print('error')
            return
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//div[@class='post-title-content__5QLz1']//span/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            detail = sel.xpath("//div[@class='post-content__4I3JT']/text()")
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')

            eles[i].click()
            i += 1
            time.sleep(2)
            # 切换到第二个窗口
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            url = browser.current_url
            while len(browser.window_handles) > 1:
                browser.switch_to.window(windows[-1])
                browser.close()
                time.sleep(3)
            browser.switch_to.window(windows[0])

            # url = "https://talent.baidu.com/jobs/social-list?search=&"+title+detail

            self.result_map[browser.current_url].append(TaskResult(title, detail, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'BaiDuCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'BaiDuCrawl start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.url) is not None:
                    continue
                txt = '【百度招聘】\n' \
                      '岗位名称：%s\n' \
                      '详情:%s\n' \
                      '链接:%s' % (data.title, data.detail, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=txt)
                except Exception as e:
                    print("mq err:",e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(data.url, '')


class TaskResult:
    def __init__(self, title, detail, url):
        self.title = title
        self.detail = detail
        self.url = url
