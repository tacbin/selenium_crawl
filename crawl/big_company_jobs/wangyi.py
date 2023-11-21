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


class WangYiCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = ["https://hr.163.com/job-list.html"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'WangYiCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WangYiCrawl start crawl..', browser.current_url)
        time.sleep(10)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='posi-list-card']")
        eles = browser.find_elements(By.XPATH,
                                     "//span[@class=' f-toe']")
        i = 0

        try:
            browser.find_elements(By.XPATH, "//div[@class='btn']")[0].click()
        except Exception as e:
            pass

        if len(eles) != len(tasks):
            QQRobot.send_to_police(['%s \n 网易招聘解析失败!任务数不一样' % browser.current_url])

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n 网易招聘解析失败!无岗位信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//span[@class=' f-toe']/text()")
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            place = sel.xpath("//span[@class='tag f-toe']/text()")
            place = place[-1] if len(place) > 0 else ''
            place = place.replace('\n', '')

            update_time = sel.xpath("//div[@class='change-show']/text()")
            update_time = update_time[0] if len(update_time) > 0 else ''
            update_time = update_time.replace('\n', '')

            category = sel.xpath("//div[@class='base-detail']/span/text()")
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
            # 切换到第二个窗口
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            url = browser.current_url
            while len(browser.window_handles) > 1:
                browser.switch_to.window(windows[-1])
                browser.close()
                time.sleep(3)
            browser.switch_to.window(windows[0])

            self.result_map[browser.current_url].append(TaskResult(title, place, update_time, url, category))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WangYiCrawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'WangYiCrawl start custom_send..', url)
            for data in self.result_map[url]:
                if CommonInstance.Redis_client.get(data.title + data.place + data.update_time) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【网易招聘】\n\n' \
                      '岗位名称：%s\n\n' \
                      '地点：%s\n\n' \
                      '部门：%s\n\n' \
                      '发布时间:%s\n\n' \
                      '链接:%s' % (data.title, data.place, data.category, data.update_time, data.url)
                try:
                    get_rabbit_mq_channel().basic_publish(exchange="", routing_key="selenium-crawl-queue",
                                                          body=str(json.dumps(data.__dict__,ensure_ascii=False)))
                except Exception as e:
                    print("mq err:", e)
                QQRobot.send_group_msg(JobGroupConstant, [txt])
                QQRobot.send_company_msg_xiaowo(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(data.title + data.place + data.update_time, '')


class TaskResult:
    def __init__(self, title, place, update_time, url, category):
        self.company = '网易招聘'
        self.title = title
        self.place = place
        self.update_time = update_time
        self.url = url
        self.category = category
