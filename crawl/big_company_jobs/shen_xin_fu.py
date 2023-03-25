# -*- coding: utf-8 -*-
import json
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


class ShenXinFuCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://hr.sangfor.com/Sociology"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'ShenXinFuCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ShenXinFuCrawl start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='x_zpPost_cardList']")
        eles = browser.find_elements(By.XPATH,
                                     "//div[@class='details']")
        i = 0
        if len(eles) != len(tasks):
            print('error')
            return

        for task in tasks:
            tasks = selector.xpath("//div[@class='x_zpPost_cardList']")
            eles = browser.find_elements(By.XPATH,
                                         "//div[@class='details']")
            task = tasks[i]


            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//h1/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            place = sel.xpath("//div[@class='city']/text()")
            place = place[-1] if len(place) > 0 else ''
            place = place.replace('\n', '')

            category = sel.xpath("//p/text()")
            category = category[0] if len(category) > 0 else ''
            category = category.replace('\n', '')

            try:
                browser.execute_script("arguments[0].scrollIntoView();", eles[i])
                time.sleep(1)
                # eles[i].click()
                browser.execute_script("arguments[0].click();", eles[i])

            except Exception as e:
                print(e)
            i += 1

            time.sleep(2)
            url = browser.current_url
            # 切换到第二个窗口
            browser.back()
            time.sleep(2)

            self.result_map[browser.current_url].append(TaskResult(title, place, url, category))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ShenXinFuCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ShenXinFuCrawl start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "http://api.tacbin.club/" + path
                txt = '【深信服招聘】\n' \
                      '岗位名称：%s\n' \
                      '地点：%s\n' \
                      '分类：%s\n' \
                      '链接:%s' % (data.title, data.place, data.category, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__)))
                except Exception as e:
                    print("mq err:", e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, place, url, category):
        self.company = '深信服招聘'
        self.title = title
        self.place = place
        self.url = url
        self.category = category
