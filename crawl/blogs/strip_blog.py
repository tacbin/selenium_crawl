# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver

from common_crawl import CommonCrawl
import time
import json

from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.constants import JobGroupConstant
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class StripBlogCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        # self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://stripe.com/blog/engineering"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'StripBlogCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'StripBlogCrawlstart crawl..',
              browser.current_url)
        time.sleep(5)

        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//article[contains(@class,'BlogIndexPost')]")

        if len(tasks) == 0:
            QQRobot.send_to_police(['%s \n StripBlog 解析失败!无解析信息' % browser.current_url])

        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//h1//a//text()")
            title = ''.join(title)
            title = title.replace('\n', '').strip()

            cate = ''

            desc = sel.xpath("//div[@class='BlogIndexPost__body']//text()")
            desc = ''.join(desc)
            desc = desc.replace('\n', '').replace('\t', '').strip()

            url = sel.xpath("//h1//a/@href")
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = 'https://stripe.com' + url

            self.result_map[browser.current_url].append(TaskResult(title, cate, desc, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'StripBlog Crawl end crawl..', browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'StripBlog Crawl start custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【StripBlog】\n\n' \
                      '标题：%s\n\n' \
                      '描述：%s\n\n' \
                      '链接:%s' % (data.title, data.desc, data.url)

                QQRobot.send_blogs([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, cate, desc, url):
        self.title = title
        self.cate = cate
        self.desc = desc
        self.url = url
