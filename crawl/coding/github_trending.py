# -*- coding: utf-8 -*-

import time

from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class GithubTrendingCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://github.com/trending"]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'GithubTrendingCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubTrendingCrawlstart crawl..',
              browser.current_url)
        time.sleep(5)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath("//article[@class='Box-row']")
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath("//h2//a/text()")
            title = '\n'.join(title)
            title = title.replace('\n', '').strip()

            language = sel.xpath("//span[@itemprop='programmingLanguage']/text()")
            language = '\n'.join(language)
            language = language.replace('\n', '').strip()

            desc = sel.xpath("//p[contains(@class,'col-9')]/text()")
            desc = '\n'.join(desc)
            desc = desc.replace('\n', '').strip()

            url = sel.xpath('//h2//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = "https://github.com/" + url.replace('//', '')

            self.result_map[browser.current_url].append(TaskResult(title, language, desc, url))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubTrendingCrawlend crawl..',
              browser.current_url)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GithubTrendingCrawlstart custom_send..', url)
            for data in self.result_map[url]:
                key = data.url
                if CommonInstance.Redis_client.get(key) is not None:
                    continue
                val = CommonInstance.Redis_client.incrby('qq')
                path = "r_qq/" + str(val)
                print(path)
                CommonInstance.Redis_client.set(path, data.url)
                data.url = "https://api.tacbin.club/" + path
                txt = '【github趋势】\n\n' \
                      '标题：%s\n\n' \
                      '描述:%s\n\n' \
                      '语言:%s\n\n' \
                      '链接:%s' % (data.title, data.desc, data.language, data.url)

                QQRobot.send_to_coding([txt])
                QQRobot.send_to_coding_xiaowo([txt])
                CommonInstance.Redis_client.set(key, '')


class TaskResult:
    def __init__(self, title, language, desc, url):
        self.title = title
        self.language = language
        self.desc = desc
        self.url = url
