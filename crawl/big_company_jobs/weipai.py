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


class WeiPaiCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://wepie-dingtalk.mokahr.com/social-recruitment/wepie/7359#/jobs?zhineng%5B0%5D=22171&zhineng%5B1%5D=107774&zhineng%5B2%5D=22168&zhineng%5B3%5D=22169&zhineng%5B4%5D=22170&zhineng%5B5%5D=22172&zhineng%5B6%5D=22173&zhineng%5B7%5D=22174&zhineng%5B8%5D=0&page=1&anchorName=jobsList&keyword="]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'WeiPaiCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiPaiCrawl  start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='container-aOp138AX_X large-yh1BjPzxqE list-oR2doUijv4']")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div[@class="title-u2qk9xX9Ie"]/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            update_time = sel.xpath('//span[@class="ellipsis-s4h2VX0z8O"]//text()')
            update_time = update_time[0] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            url = sel.xpath('//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = "https://wepie-dingtalk.mokahr.com/social-recruitment/wepie/7359" + url

            self.result_map[browser.current_url].append(TaskResult(title, update_time, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiPaiCrawl  end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WeiPaiCrawl  start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "http://api.tacbin.club/" + path
                txt = '【武汉微派招聘】\n' \
                      '岗位名称：%s\n' \
                      '更新时间:%s\n' \
                      '地点：武汉\n' \
                      '链接:%s' % (data.title, data.update_time, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(data))
                except Exception as e:
                    print("mq err:", e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, update_time, url):
        self.title = title
        self.update_time = update_time
        self.url = url
