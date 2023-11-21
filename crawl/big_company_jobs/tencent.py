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


class TencentCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://careers.tencent.com/en-us/search.html?query=ot_40001001,ot_40001002,ot_40001003,ot_40001004,ot_40001005,ot_40001006,co_1&sc=1",
            "https://careers.tencent.com/en-us/search.html?query=ot_40006,co_1&sc=1",
            "https://careers.tencent.com/en-us/search.html?query=co_1,ot_40003001,ot_40003002,ot_40003003&sc=1"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'TencentCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="recruit-list"]')
        eles = browser.find_elements(By.XPATH,
                                     "//span[@class='job-recruit-title']")
        i = 0
        if len(eles) != len(tasks):
            QQRobot.send_to_police(['%s \n 腾讯招聘解析失败,len(eles)!=len(tasks)' % browser.current_url])

        ck_bt = browser.find_elements(By.XPATH, "//div[@class='cookie-btn']")
        if len(ck_bt) >= 1:
            try:
                ck_bt[0].click()
            except Exception as e:
                QQRobot.send_to_police(['%s \n 腾讯招聘点击按钮报错!,e:%s' % (browser.current_url, str(e))])
                print("click err:", e)
        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n 腾讯招聘解析失败!无岗位信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//span[@class="job-recruit-title"]/text()')
            title = '\n'.join(title)
            title = title.replace('\n', '')

            cate = sel.xpath('//p[@class="recruit-tips"]//text()')
            cate = '; '.join(cate)
            cate = cate.replace('\n', '')

            detail = sel.xpath('//p[@class="recruit-text"]//text()')
            detail = '\n'.join(detail)
            detail = detail.replace('\n', '')

            try:
                eles[i].click()
            except Exception as e:
                print(e)
            time.sleep(2)
            # 切换到第二个窗口 获取url
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            url = browser.current_url
            while len(browser.window_handles) > 1:
                browser.switch_to.window(windows[-1])
                browser.close()
                time.sleep(3)
            browser.switch_to.window(windows[0])

            self.result_map[browser.current_url].append(TaskResult(title, detail, cate, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【腾讯招聘】\n\n' \
                      '岗位名称：%s\n\n' \
                      '类目:%s\n\n' \
                      '详情：%s\n\n' \
                      '链接:%s' % (data.title, data.cate, data.detail, data.url)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                QQRobot.send_company_msg_xiaowo(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__, ensure_ascii=False)))
                except Exception as e:
                    print("mq err:", e)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'TencentCrawl   end custom_send..')


class TaskResult:
    def __init__(self, title, detail, cate, url):
        self.company = '腾讯招聘'
        self.title = title
        self.detail = detail
        self.cate = cate
        self.url = url
