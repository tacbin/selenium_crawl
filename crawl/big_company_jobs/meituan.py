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


class MeiTuanCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://zhaopin.meituan.com/web/social"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'MeiTuanCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'MeiTuanCrawl start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='position_list_item cursor_pointer']")
        eles = browser.find_elements(By.XPATH,
                                     "//div[@class='position_list_item_content_left']")
        i = 0
        if len(eles) != len(tasks):
            print('error')
            return

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//div[@class='title hidden-ellipsis']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            place = sel.xpath("//div[@class='zp_clamp_string_inner']/span/text()")
            place = place[-1] if len(place) > 0 else ''
            place = place.replace('\n', '')

            update_time = sel.xpath("//div[@class='split_line_box_item']/span/text()")
            update_time = update_time[1] if len(update_time) > 1 else ''
            update_time = update_time.replace('\n', '')

            category = sel.xpath("//div[@class='split_line_box_item']/span/text()")
            category = category[2] if len(category) > 2 else ''
            category = category.replace('\n', '')

            detail = sel.xpath("//div[@class='desc hidden-ellipsis']/text()")
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

            self.result_map[browser.current_url].append(TaskResult(title, place, update_time, url, category, detail))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'MeiTuanCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'MeiTuanCrawl start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.title + data.place + data.update_time) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【美团招聘】\n' \
                      '岗位名称：%s\n' \
                      '地点：%s\n' \
                      '事业群：%s\n' \
                      '详情：%s\n' \
                      '发布时间:%s\n' \
                      '链接:%s' % (data.title, data.place, data.category, data.detail, data.update_time, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__,ensure_ascii=False)))
                except Exception as e:
                    print("mq err:", e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(data.title + data.place + data.update_time, '')


class TaskResult:
    def __init__(self, title, place, update_time, url, category, detail):
        self.company = '美团招聘'
        self.title = title
        self.place = place
        self.update_time = update_time
        self.url = url
        self.category = category
        self.detail = detail
