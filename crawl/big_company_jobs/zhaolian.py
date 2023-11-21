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


class ZhaoLianCrawler(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://wecruit.hotjob.cn/SU61027bb10dcad47a7e23e040/pb/social.html"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'ZhaoLianCrawler'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ZhaoLianCrawler start crawl..',
              browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="list-row-item"]')
        eles = browser.find_elements(By.XPATH,
                                     '//div[@class="list-row-item"]//div[@class="list-cell pos-name"]')
        i = 0
        if len(eles) != len(tasks):
            if len(eles) != len(tasks):
                QQRobot.send_to_police(['%s \n 招联招聘解析失败!任务数不一样' % browser.current_url])
            return

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n 招联招聘解析失败!无岗位信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//span[@class='list-cell-span']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            cate = sel.xpath("//span[@class='list-cell-span']/text()")
            cate = cate[1] if len(cate) > 0 else ''
            cate = cate.replace('\n', '')

            place = sel.xpath("//span[@class='list-cell-span']/text()")
            place = place[2] if len(place) > 0 else ''
            place = place.replace('\n', '')

            update_time = sel.xpath("//span[@class='list-cell-span']/text()")
            update_time = update_time[3] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            eles[i].click()
            i += 1
            time.sleep(2)
            # 切换到第二个窗口
            windows = browser.window_handles

            url = browser.current_url
            while len(browser.window_handles) > 1:
                browser.switch_to.window(windows[-1])
                browser.close()
                time.sleep(3)
            browser.switch_to.window(windows[0])

            self.result_map[browser.current_url].append(TaskResult(title, cate, place, update_time, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ZhaoLianCrawler end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ZhaoLianCrawler start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【招联金融招聘】\n\n' \
                      '岗位名称：%s\n\n' \
                      '类别：%s\n\n' \
                      '地点：%s\n\n' \
                      '发布时间:%s\n\n' \
                      '链接:%s' % (data.title, data.cate, data.place, data.update_time, data.url)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                QQRobot.send_company_msg_xiaowo(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__, ensure_ascii=False)))
                except Exception as e:
                    print("mq err:", e)


class TaskResult:
    def __init__(self, title, cate, place, update_time, url):
        self.company = '招联金融招聘'
        self.title = title
        self.cate = cate
        self.place = place
        self.update_time = update_time
        self.url = url
