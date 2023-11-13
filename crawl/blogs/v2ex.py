# -*- coding: utf-8 -*-
import json
import os
import time

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class V2exCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://www.v2ex.com/?tab=all"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'V2exCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'V2exCrawl   start crawl..', browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//div[@class='cell item']//td//a[@class='topic-link']")
        eles = browser.find_elements(By.XPATH,
                                     "//div[@class='cell item']//td//a[@class='topic-link']")

        if len(eles) != len(tasks):
            QQRobot.send_to_police(['%s \n V2ex解析失败,len(eles)!=len(tasks)' % browser.current_url])
            return

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n V2ex解析失败!无卡片信息' % browser.current_url])
            return
        count = 0
        for task in tasks:
            count += 1
            if count > 10:
                break
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//a/text()')
            title = '\n'.join(title)
            title = title.replace('\n', '')

            url = sel.xpath('//a/@href')
            url = '\n'.join(url)
            url = url.replace('\n', '')
            url = 'https://www.v2ex.com' + url
            url = url.split('#')[0]
            if CommonInstance.Redis_client.get(url) is not None:
                continue
            browser.execute_script(f"location.href='{url}';")

            time.sleep(3)
            self.is_save_img = True
            self.save_img(browser, 0, title)
            self.is_save_img = False

            # 切换到第二个窗口
            browser.back()
            time.sleep(3)

            self.result_map[browser.current_url].append(TaskResult(title, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'V2exCrawl   end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'V2exCrawl   start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【V2ex blog】\n\n' \
                      '标题：%s\n\n' \
                      '链接:%s' % (data.title, data.url)
                dirs = self.get_file_path()

                file_path = os.path.join(dirs, data.title + ".png")

                QQRobot.send_image_blogs([file_path])
                QQRobot.send_blogs(JobGroupConstant, [txt])
                CommonInstance.Redis_client.set(key, '')

        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'V2exCrawl   end custom_send..')


class TaskResult:
    def __init__(self, title, url):
        self.title = title
        self.url = url
