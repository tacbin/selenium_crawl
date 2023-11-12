# -*- coding: utf-8 -*-

import time

from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class GithubProjectsCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://github.com/shenghui0779/yiigo",
            "https://github.com/yinggaozhen/awesome-go-cn",
            "https://github.com/chatwoot/chatwoot",
            "https://github.com/krahets/hello-algo",
            "https://github.com//alibaba/flutter-go",
            "https://github.com//APIs-guru/openapi-directory",
            "https://github.com//TheAlgorithms/Python",
            "https://github.com//lobehub/lobe-chat",
        ]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'GithubProjectsCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubProjectsCrawlstart crawl..',
              browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//body")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//strong//a/text()")
            title = '\n'.join(title)
            title = title.replace('\n', '').strip()

            language = sel.xpath("//li[@class='d-inline']//span[contains(@class,'color-fg-default')]/text()")
            language = '; '.join(language)
            language = language.replace('\n', '').strip()

            desc = sel.xpath("//div[@class='BorderGrid-cell']//p/text()")
            desc = '\n'.join(desc)
            desc = desc.replace('\n', '').strip()

            tag = sel.xpath("//a[contains(@class,'f6 Link--secondary')]/text()")
            tag = '\n'.join(tag)
            tag = tag.replace('\n', '').strip()

            url = browser.current_url

            self.result_map[browser.current_url].append(TaskResult(title, language, desc, tag, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubProjectsCrawlend crawl..',
              browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubProjectsCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.tag
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【项目更新啦!!!】\n\n' \
                      '标题：%s\n\n' \
                      '描述:%s\n\n' \
                      '语言:%s\n\n' \
                      '链接:%s' % (data.title, data.desc, data.language, data.url)

                QQRobot.send_to_coding([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, language, desc, tag, url):
        self.title = title
        self.language = language
        self.desc = desc
        self.tag = tag
        self.url = url
