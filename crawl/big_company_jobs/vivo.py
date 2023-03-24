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


class VivoCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://hr.vivo.com/wt/vivo/web/templet1000/index/corpwebPosition1000vivo!gotoPostListForAjax?brandCode=1&useForm=0&recruitType=2&showComp=true"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'VivoCrawl  '
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'VivoCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="job-item"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//h4[@class="job-title"]/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')
            title = title.replace(' ', '')

            cate = sel.xpath('//div[@class="job-info"]//text()')
            cate = cate[0] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')
            cate = cate.replace(' ', '')

            detail = sel.xpath('//div[@class="job-description introduceDetail"]//text()')
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')
            detail = detail.replace(' ', '')

            url = 'https://hr.vivo.com/wt/vivo/web/templet1000/index/corpwebPosition1000vivo!gotoPostListForAjax?brandCode=1&useForm=0&recruitType=2&showComp=true&&' + title + cate

            self.result_map[browser.current_url].append(TaskResult(title, detail, cate, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'VivoCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'VivoCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url.split("&&")[0]
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, key)
                data.url = "http://api.tacbin.club/" + path
                txt = '【VIVO招聘】\n' \
                      '岗位名称：%s\n' \
                      '类目:%s\n' \
                      '详情:%s\n' \
                      '链接:%s' % (data.title, data.cate, data.detail, data.url.split("&&")[0])
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(data))
                except Exception as e:
                    print("mq err:",e)


class TaskResult:
    def __init__(self, title, detail, cate, url):
        self.title = title
        self.detail = detail
        self.cate = cate
        self.url = url
