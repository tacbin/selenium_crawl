# -*- coding: utf-8 -*-
import os
import platform
import smtplib
import time
import uuid
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

import selenium
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from common.common_instantce import CommonInstance
from common.email import EmailInfo, AttachInfo


class CommonCrawl:
    def __init__(self):
        self.urls = []
        self.mode = 0
        self.file_location = ''
        self.email_info = EmailInfo()
        self.__img_path = []
        self.is_save_img = False

    def run(self, *args):
        # 使用 fire_fox 的 WebDriver
        fire_fox_options = Options()
        # 代理
        # proxy = self.__get_proxy()
        # fire_fox_options.add_argument('--proxy-server=' + proxy)
        fire_fox_options.add_argument('--headless')
        if platform.system().lower() == 'linux':
            browser = selenium.webdriver.Firefox(options=fire_fox_options, executable_path='./geckodriver')
            fire_fox_options.arguments.remove('--headless')
        else:
            browser = selenium.webdriver.Firefox(options=fire_fox_options)
        browser = self.before_crawl(args, browser)
        for i in range(0, len(self.urls)):
            browser.get(self.urls[i])
            # save img
            self.__save_img(browser, i, "normal")
            # parse html
            time.sleep(1.5)
            self.parse(browser)
            # page search
            self.__next_click(browser)
        time.sleep(10)
        browser.close()
        # 处理结果的策略
        self.before_send()
        if self.mode == 0:
            self.__send_email()
        elif self.mode == 1:
            self.custom_send()
        else:
            pass

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        return browser

    def parse(self, browser: WebDriver):
        pass

    def before_send(self):
        pass

    def custom_send(self):
        pass

    def __send_email(self):
        if self.email_info is None:
            return
        sender = '2840498397@qq.com'
        receivers = self.email_info.receivers
        if len(receivers) == 0:
            return

        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = Header("tacbin", 'utf-8')
        subject = self.email_info.subject
        message['Subject'] = Header(subject, 'utf-8')

        # 邮件正文内容
        message.attach(MIMEText(self.email_info.content, 'html', 'utf-8'))
        for attach_info in self.email_info.attaches:
            if not isinstance(attach_info, AttachInfo):
                return
            # 构造附件
            att = MIMEText(open(attach_info.file_location, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename="%s"' % attach_info.file_name
            message.attach(att)
        try:
            smtp = smtplib.SMTP_SSL(host='smtp.qq.com')
            smtp.ehlo("smtp.qq.com")
            smtp.login(sender, 'yfxehwhnrxqadche')
            smtp.sendmail(sender, receivers, message.as_string())
            smtp.close()
        except smtplib.SMTPException as e:
            print(e)

    def get_next_elements(self, browser: WebDriver) -> List[WebElement]:
        # return browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
        return []

    def __save_img(self, browser: WebDriver, i: int, prefix: str):
        if not self.is_save_img:
            return
        time.sleep(2)
        # 用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
        width = browser.execute_script("return document.documentElement.scrollWidth")
        height = browser.execute_script("return document.documentElement.scrollHeight")
        # 将浏览器的宽高设置成刚刚获取的宽高
        browser.set_window_size(width, height)
        dirs = self.get_file_path()
        if not os.path.exists(dirs):
            os.makedirs(dirs, mode=0o1777)
        file_path = os.path.join(dirs, prefix + "_" + str(i) + "_" + str(uuid.uuid4()) + ".png")
        browser.get_screenshot_as_file(file_path)
        self.__img_path.append(file_path)

    def __next_click(self, browser: WebDriver):
        elements = self.get_next_elements(browser)
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
            self.__save_img(browser, i, "click")
            # parse html
            time.sleep(1.5)
            self.parse(browser)
            # next page
            elements = self.get_next_elements(browser)
            i += 1

    def get_file_path(self):
        return os.path.join('.', self.file_location)

    def get_img_local_path(self):
        return self.__img_path

    # def __get_proxy(self):
    #     return requests.get("http://127.0.0.1:5010/get/").text
