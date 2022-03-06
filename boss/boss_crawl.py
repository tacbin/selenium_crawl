from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from common_crawl import CommonCrawl


class BossCrawl(CommonCrawl):
    def __init__(self, key_word: str):
        super().__init__()
        url = 'https://www.zhipin.com/job_detail/?query=%s&city=101280600&source=8' % key_word
        self.urls = [url]
        self.mode = 0
        self.img_location = 'boss_%s' % key_word

    def before_crawl(self):
        pass

    def parse(self, browser: WebDriver):
        print(browser.page_source)

    def send_email(self):
        pass

    def get_next_elements(self, browser: WebDriver) -> List[WebElement]:
        return browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
