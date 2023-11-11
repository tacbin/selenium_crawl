# -*- coding: utf-8 -*-
import json
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
from selenium import webdriver
from selenium.webdriver import Proxy, FirefoxProfile
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from common.common_instantce import CommonInstance
from common.email import EmailInfo, AttachInfo


# browser = None


class CommonCrawl:
    def __init__(self):
        self.urls = []
        self.mode = 0
        self.file_location = ''
        self.email_info = EmailInfo()
        self.__img_path = []
        self.is_save_img = False
        # self.channel = get_rabbit_mq_channel()
        self.is_run = True
        self.show_head = True
        self.use_proxy = False

    def run(self, *args):
        if not self.is_run:
            return
        # 代理置为空
        browser = None
        try:
            # 使用 fire_fox 的 WebDriver
            fire_fox_options = Options()
            proxy = Proxy()
            profile = FirefoxProfile()

            addr = "127.0.0.1:10809"
            if self.use_proxy:
                if platform.system().lower() == 'linux':
                    addr = "192.168.3.19:9999"

                proxy.proxy_type = ProxyType.MANUAL
                proxy.http_proxy = addr
                proxy.ssl_proxy = addr

                profile.set_proxy(proxy)

            if browser is None:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "start to init browser")
                if platform.system().lower() == 'linux':
                    fire_fox_options.add_argument('--headless')
                    browser = selenium.webdriver.Firefox(firefox_profile=profile, options=fire_fox_options,
                                                         executable_path='./geckodriver'
                                                         )
                elif platform.system().lower() == 'darwin':
                    if not self.show_head:
                        fire_fox_options.add_argument('--headless')
                    browser = selenium.webdriver.Firefox(firefox_profile=profile, options=fire_fox_options,
                                                         executable_path='./mac_geckodriver'
                                                         )
                else:
                    if not self.show_head:
                        fire_fox_options.add_argument('--headless')
                    browser = selenium.webdriver.Firefox(firefox_profile=profile, options=fire_fox_options)

            else:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "skip to init browser")
            browser = self.before_crawl(args, browser)
            for i in range(0, len(self.urls)):
                time.sleep(5)
                browser.execute_script(f"location.href='{self.urls[i]}';")
                time.sleep(2)
                # save img
                self.save_img(browser, i, "normal")
                # parse html
                time.sleep(3)
                self.parse(browser)
                # page search
                self.__next_click(browser)
                time.sleep(2)
                self.__next_url(browser)

            time.sleep(10)
            # browser.close()
            # 处理结果的策略
            self.before_send()
            if self.mode == 0:
                self.__send_email()
            elif self.mode == 1:
                self.custom_send()
            else:
                pass
            if browser is None:
                return
            browser.close()
        except Exception as e:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'common crawl exception:', e)
            try:
                if browser is None:
                    return
                browser.close()
            except Exception as e:
                print("close err", e)

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        return browser

    def parse(self, browser: WebDriver):
        pass

    def before_send(self):
        pass

    def custom_send(self):
        pass

    def get_file_name(self):
        return str(uuid.uuid4())

    def get_next_click_elements(self, browser: WebDriver) -> List[WebElement]:
        # return browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
        return []

    def get_next_urls(self, browser: WebDriver) -> List[str]:
        return []

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

    def save_img(self, browser: WebDriver, i: int, file_name: str):
        if not self.is_save_img:
            return
        # 用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
        width = browser.execute_script("return document.documentElement.scrollWidth")
        height = browser.execute_script("return document.documentElement.scrollHeight")
        # 将浏览器的宽高设置成刚刚获取的宽高
        browser.set_window_size(width, height)
        dirs = self.get_file_path()
        if not os.path.exists(dirs):
            os.makedirs(dirs, mode=0o1777)
        file_path = os.path.join(dirs, file_name + ".png")
        browser.get_screenshot_as_file(file_path)
        self.__img_path.append(file_path)
        time.sleep(2)

    def __next_click(self, browser: WebDriver):
        elements = self.get_next_click_elements(browser)
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
            self.save_img(browser, i, "click")
            # parse html
            time.sleep(1.5)
            self.parse(browser)
            # next page
            elements = self.get_next_click_elements(browser)
            i += 1

    def __next_url(self, browser: WebDriver):
        urls = self.get_next_urls(browser)
        if len(urls) == 0:
            return
        for i in range(0, len(urls)):
            browser.execute_script(f"location.href='{urls[i]}';")
            # save img
            self.save_img(browser, i, "normal")
            # parse html
            time.sleep(1.5)
            self.parse(browser)

    def get_file_path(self):
        return os.path.join('.', self.file_location)

    def get_img_local_path(self):
        return self.__img_path

    # def __get_proxy(self):
    #     return requests.get("http://192.168.1.1:5010/get/").text

    def load_cookie(self, browser: WebDriver, file_name: str):
        cookies = CommonInstance.Redis_client.get(file_name)
        result = []
        if cookies is not None:
            list_cookies = json.loads(cookies)
            for c in list_cookies:
                if "expiry" in c:
                    continue
                result.append(c)
            return result
        return result

        # if os.path.exists(file_name):
        #     with open(file_name, 'r', encoding='utf-8') as f:
        #         list_cookies = json.loads(f.read())
        #         result = []
        #         for c in list_cookies:
        #             if "expiry" in c:
        #                 continue
        #             result.append(c)
        #         return result

    def save_cookie(self, browser: WebDriver, file_name: str):
        cookies = browser.get_cookies()
        json_cookies = json.dumps(cookies)
        # with open(file_name, 'w') as f:
        # f.write(json_cookies)
        CommonInstance.Redis_client.set(file_name, json_cookies)
