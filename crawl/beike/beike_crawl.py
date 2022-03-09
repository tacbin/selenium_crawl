# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver

from common_crawl import CommonCrawl


class BeiKeCrawl(CommonCrawl):
    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = ["https://sz.ke.com/ershoufang/rs%E5%B8%83%E5%90%89/"]
        self.mode = 0
        self.file_location = 'boss_crawl'
        return browser

    def parse(self, browser: WebDriver):
        print(browser.page_source)

    def before_send_email(self):
        pass
