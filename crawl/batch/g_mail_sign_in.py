# -*- coding: utf-8 -*-
import random
import time

from lxml import html
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common_crawl import CommonCrawl


class GEmailSignInCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.use_proxy = True

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.result_map = {}
        self.urls = [
            "https://accounts.google.com/v3/signin/identifier?hl=zh-cn&ifkv=AVQVeyxL3wAsiaqIPi_b-cNAb-IpNlFDW-uzmcZOlZeBLcC1nHkahbtHFSQQ7cHn7fpJtw4LO8GCEA&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S1359662542%3A1700395115739622&theme=glif",
        ]
        for url in self.urls:
            self.result_map[url] = []

        self.file_location = 'GEmailSignInCrawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GEmailSignInCrawlstart crawl..',
              browser.current_url)
        time.sleep(10)
        # 用户信息填写
        # GEmailSignInCrawl.user_info(browser)
        # time.sleep(10)

        browser.find_elements(By.XPATH, "//input")[0].send_keys("gardinerherodoto@gmail.com")
        time.sleep(5)
        browser.find_elements(By.XPATH, '//button')[-2].click()
        time.sleep(10)

        browser.find_elements(By.XPATH, "//input")[0].send_keys("89xxyrfqdgxonf")
        time.sleep(5)
        browser.find_elements(By.XPATH, '//button')[-2].click()
        time.sleep(10)
        #
        # emails = ["2840498397@qq.com","2571761894@qq.com","oh.ulaula@gmail.com","tacbin.steam.001@gmail.com"]
        # email = random.randint(0, 2)
        # browser.find_elements(By.XPATH, '//input[@aria-label="辅助邮箱地址"]')[0].send_keys(emails[email])
        # time.sleep(10)
        #
        #
        # browser.find_elements(By.XPATH, "//span[@jsname='V67aGc']")[0].send_keys(emails[email])
        time.sleep(7200)


        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GEmailSignInCrawlend crawl..',
              browser.current_url)

    @staticmethod
    def user_info(browser: WebDriver):
        browser.find_element_by_id("firstName").send_keys("MoondyLi")
        time.sleep(10)
        browser.find_elements(By.XPATH, '//button')[0].click()
        time.sleep(10)
        year_day = browser.find_elements(By.XPATH,
                                         "//input[@class='whsOnd zHQkBf']")
        year = year_day[0]
        day = year_day[1]

        year.send_keys("199" + str(random.randint(0, 9)))
        time.sleep(5)
        month = random.randint(2, 12)
        browser.find_elements(By.XPATH, "//select[@class='UDCCJb']//option")[month].click()
        time.sleep(5)
        day.send_keys(str(random.randint(1, 30)))
        time.sleep(5)
        browser.find_elements(By.XPATH, "//select[@id='gender']//option")[2].click()
        time.sleep(5)

        browser.find_elements(By.XPATH, '//button')[0].click()
        time.sleep(10)

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'GEmailSignInCrawlstart custom_send..', url)
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
