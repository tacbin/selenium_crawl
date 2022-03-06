import os
import time
from typing import List

import selenium
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox import webdriver


class CommonCrawl:
    def __init__(self):
        self.urls = []
        self.obj_dic = {}
        self.mode = 0
        self.img_location = ''

    def run(self):
        self.before_crawl()
        # 使用 fire_fox 的 WebDriver
        fire_fox_options = Options()
        # fire_fox_options.add_argument('--headless')
        browser = webdriver.Firefox(options=fire_fox_options)
        for i in range(0, len(self.urls)):
            browser.get(self.urls[i])
            # save img
            self.__save_img(browser, i)
            # parse html
            self.parse(browser)
            # page search
            self.__next_click(browser)
        browser.close()
        # 处理结果的策略
        if self.mode == 0:
            self.send_email()
        else:
            pass

    def before_crawl(self):
        pass

    def parse(self, browser: WebDriver):
        pass

    def send_email(self):
        pass

    def get_next_elements(self, browser: WebDriver) -> List[WebElement]:
        # return browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
        return []

    def __save_img(self, browser: WebDriver, i: int):
        if self.img_location is None:
            return
        time.sleep(2)
        # 用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
        width = browser.execute_script("return document.documentElement.scrollWidth")
        height = browser.execute_script("return document.documentElement.scrollHeight")
        # 将浏览器的宽高设置成刚刚获取的宽高
        browser.set_window_size(width, height)
        browser.get_screenshot_as_file(os.path.join(self.img_location, str(i), "_img.png"))

    def __next_click(self, browser: WebDriver):
        elements = self.get_next_elements()
        if len(elements) == 0:
            return
        current_url = browser.current_url
        i = 0
        while len(elements) > 0:
            elements[0].click()
            if current_url == browser.current_url:
                break
            current_url = browser.current_url
            # save img
            self.__save_img(browser, i)
            # parse html
            self.parse(browser)
            # next page
            elements = self.get_next_elements()
            i += 1
