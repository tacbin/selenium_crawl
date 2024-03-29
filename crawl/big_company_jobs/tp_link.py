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


class TpLinkCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://hr.tp-link.com.cn/socialJobList?jobId=0&jobDirection=0&workPlace=0&currentPage=1&keyword="]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'TpLinkCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TpLinkCrawl start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="line ng-star-inserted"]')

        i = 0
        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n tp link招聘解析失败!无岗位信息' % browser.current_url])

        while i < len(tasks):
            page = browser.page_source
            etree = html.etree
            selector = etree.HTML(page)

            eles = browser.find_elements(By.XPATH,
                                         '//div[@class="line ng-star-inserted"]//div[@class="box"]')
            tasks = selector.xpath('//div[@class="line ng-star-inserted"]')
            task = tasks[i]

            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div[@class="line ng-star-inserted"]//div[@class="box"]//p/text()')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath('//div[@class="line ng-star-inserted"]//div[@class="box"]//p/text()')
            cate = cate[1] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            place = sel.xpath('//div[@class="line ng-star-inserted"]//div[@class="box"]//p/text()')
            place = place[-1] if len(place) > 0 else ''
            place = place.replace('\n', '')

            eles[i * 3].click()
            i += 1
            time.sleep(1)
            url = browser.current_url
            time.sleep(1)
            browser.back()
            time.sleep(10)

            self.result_map[browser.current_url].append(TaskResult(title, cate, place, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TpLinkCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TpLinkCrawl start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【TpLink招聘】\n\n' \
                      '岗位名称：%s\n\n' \
                      '类别：%s\n\n' \
                      '地点：%s\n\n' \
                      '链接:%s' % (data.title, data.cate, data.place, data.url)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                QQRobot.send_company_msg_xiaowo(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__,ensure_ascii=False)))
                except Exception as e:
                    print("mq err:",e)


class TaskResult:
    def __init__(self, title, cate, place, url):
        self.company = 'TpLink招聘'
        self.title = title
        self.cate = cate
        self.place = place
        self.url = url
