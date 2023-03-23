# -*- coding: utf-8 -*-
import time
from telnetlib import EC

import miraicle
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class KuaiShouCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://zhaopin.kuaishou.cn/#/official/social/?workLocationCode=domestic"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'KuaiShouCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'KuaiShouCrawl   start crawl..',
              browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)

        i = 0

        tasks = selector.xpath('//tr[@class="ant-table-row ant-table-row-level-0"]')
        while i < len(tasks):
            page = browser.page_source
            etree = html.etree
            selector = etree.HTML(page)

            tasks = selector.xpath('//tr[@class="ant-table-row ant-table-row-level-0"]')
            task = tasks[i]
            eles = browser.find_elements(By.XPATH,
                                         "//tr//td")

            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//td/div/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath('//td//text()')
            cate = cate[1] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            place = sel.xpath('//td//text()')
            place = place[2] if len(place) > 0 else ''
            place = place.replace('\n', '')

            experience = sel.xpath('//td//text()')
            experience = experience[3] if len(experience) > 0 else ''
            experience = experience.replace('\n', '')

            update_time = sel.xpath('//td//text()')
            update_time = update_time[4] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            eles[i * 6].click()
            i += 1
            time.sleep(1)
            url = browser.current_url
            time.sleep(1)
            browser.back()
            time.sleep(2)

            self.result_map[browser.current_url].append(TaskResult(title, place, cate, experience, update_time, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'KuaiShouCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'KuaiShouCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(
                        "ks_" + data.title + data.experience + data.place + data.update_time) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "http://api.tacbin.club" + path
                txt = '【快手招聘】\n' \
                      '岗位名称：%s\n' \
                      '类目:%s\n' \
                      '工作经验:%s\n' \
                      '地点：%s\n' \
                      '更新时间：%s\n' \
                      '链接:%s' % (data.title, data.cate, data.experience, data.place, data.update_time, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=txt)
                except Exception as e:
                    print("mq err:",e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set("ks_" + data.title + data.experience + data.place + data.update_time,
                                                '')


class TaskResult:
    def __init__(self, title, place, cate, experience, update_time, url):
        self.title = title
        self.place = place
        self.cate = cate
        self.url = url
        self.experience = experience
        self.update_time = update_time
