# -*- coding: utf-8 -*-
import time
import json
import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class ByteDanceCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://jobs.bytedance.com/experienced/position?keywords=&category=6704215862557018372&location=CT_128&project=&type=&job_hot_flag=&current=1&limit=300&functionCategory=",
            "https://jobs.bytedance.com/experienced/position?keywords=&category=6704215882438019342%2C6704215955154667787%2C6704215961064442123%2C6704216001937934599%2C6704216057269192973%2C6704216853931100430%2C6850051246221429006&location=CT_128&project=&type=&job_hot_flag=&current=1&limit=300&functionCategory="]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'ByteDanceCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ByteDanceCrawlstart crawl..', browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='listItems__1q9i5']/a")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//span[@class='positionItem-title-text']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            detail = sel.xpath("//div[@class='jobDesc__3ZDgU positionItem-jobDesc']/text()")
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')

            job_id = sel.xpath("//span[@class='infoText__aS5hY']/text()")
            job_id = job_id[-1] if len(job_id) > 0 else ''
            job_id = job_id.replace('\n', '')

            url = sel.xpath('//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = "https://jobs.bytedance.com" + url.replace('//', '')

            self.result_map[browser.current_url].append(TaskResult(title, detail, job_id, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ByteDanceCrawlend crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ByteDanceCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "http://api.tacbin.club/" + path
                txt = '【字节跳动招聘】\n' \
                      '岗位名称：%s\n' \
                      '详情:%s\n' \
                      '%s\n' \
                      '链接:%s' % (data.title, data.detail, data.job_id, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__)))
                except Exception as e:
                    print("mq err:",e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, detail, job_id, url):
        self.title = title
        self.detail = detail
        self.job_id = job_id
        self.url = url
