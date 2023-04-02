# -*- coding: utf-8 -*-
import json
import platform
import threading
import time

import selenium
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


class MessageInfo:
    def __init__(self):
        self.nick_name = ''
        # 0是加入，1是发消息
        self.msg_type = 0
        self.msg = ''
        self.image = ''


def send_to_mq(msg_info: MessageInfo):
    try:
        if msg_info.nick_name is None or len(msg_info.nick_name) == 0:
            return
        data = json.dumps(msg_info.__dict__, ensure_ascii=False)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send mq data:', data)
        get_rabbit_mq_channel().basic_publish(exchange="", routing_key="dou-yin-queue",
                                              body=data)
    except Exception as e:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send mq exception:', e)


def set_user_image(browser: WebDriver, msg_info: MessageInfo):
    page = browser.page_source
    etree = html.etree
    selector = etree.HTML(page)
    image = selector.xpath("//div[@class='p-0+JvaK nsOPFX+X']//img[@class='qCM610OQ']/@src")
    name = selector.xpath("//div[@class='_7KeH6hPD']/text()")

    image = get_first_one_or_empty(image)
    name = get_first_one_or_empty(name)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), name, image)
    CommonInstance.name_image_dic[name] = image
    msg_info.image = CommonInstance.name_image_dic[msg_info.nick_name]
    if len(msg_info.image) == 0:
        return
    blank_elements = browser.find_elements(By.XPATH, "//div[@class='_1oBXuWfc']")
    blank_elements[0].click()

    send_to_mq(msg_info)
    # 点击未读消息
    blank_elements = browser.find_elements(By.XPATH, "//div[@class='_1oBXuWfc']")
    blank_elements[0].click()


class DouYinLiveCrawl(CommonCrawl):
    def __init__(self, live_url):
        super().__init__()
        self.live_url = live_url

        CommonInstance.voices_dict = {}
        CommonInstance.users_dict = {}
        CommonInstance.name_image_dic = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = [self.live_url]
        self.mode = 1
        self.file_location = 'dou_yin_live_crawl'
        self.is_save_img = False
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'dou_yin_live_crawl parse start crawl..',
              browser.current_url)
        # 开辟查看新用户的进程
        mq_thread = NewUserThreadControl(self.live_url)
        mq_thread.start()
        while True:

            try:
                unread_elements = browser.find_elements(By.XPATH,
                                                        "//div[@class='webcast-chatroom___unread-tips webcast-chatroom___unread']")
                if len(unread_elements) > 0:
                    unread_elements[0].click()
                    time.sleep(0.01)
                blank_elements = browser.find_elements(By.XPATH, "//div[@class='_1oBXuWfc']")
                blank_elements[0].click()
                msg_info = MessageInfo()
                page = browser.page_source
                etree = html.etree
                selector = etree.HTML(page)
                voices = selector.xpath(
                    "//div[@class='webcast-chatroom___items']//div[@class='webcast-chatroom___item webcast-chatroom___enter-done']")
                i = len(voices) - 1
                while i > 0:
                    v = voices[i]
                    i = i - 1
                    sel = etree.HTML(etree.tostring(v, method='html'))
                    nick_name = sel.xpath('//span[@class="tfObciRM"]/text()')
                    msg = sel.xpath('//span[@class="webcast-chatroom___content-with-emoji-text"]/text()')

                    nick_name = get_first_one_or_empty(nick_name)
                    msg = get_first_one_or_empty(msg)

                    unique_key = nick_name + '-' + msg

                    if unique_key in CommonInstance.voices_dict:
                        continue
                    if len(CommonInstance.voices_dict) > 10000:
                        CommonInstance.voices_dict = {}
                    CommonInstance.voices_dict[unique_key] = ''
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), nick_name, msg)
                    msg_info.msg_type = 1
                    msg_info.msg = msg
                    msg_info.nick_name = nick_name
                    voices_elements = browser.find_elements(By.XPATH,
                                                            '//div[@class="webcast-chatroom___items"]//div[@class="webcast-chatroom___item webcast-chatroom___enter-done"]//span[@class="tfObciRM"]')
                    if nick_name not in CommonInstance.name_image_dic:
                        if len(voices_elements) == 0:
                            continue
                        for e in voices_elements:
                            line_name = e.text.strip().split('：')[0]
                            if line_name == nick_name:
                                e.click()
                                time.sleep(0.1)
                                set_user_image(browser, msg_info)
                    else:
                        msg_info.image = CommonInstance.name_image_dic[nick_name]
                        send_to_mq(msg_info)

            except Exception as e:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'dou_yin crawl exception:', e)


class NewUserThreadControl(threading.Thread):
    def __init__(self, live_url: str):
        threading.Thread.__init__(self)
        self.live_url = live_url

    def run(self):
        # 使用 fire_fox 的 WebDriver
        fire_fox_options = Options()
        if platform.system().lower() == 'linux':
            fire_fox_options.add_argument('--headless')
            browser = selenium.webdriver.Firefox(options=fire_fox_options, executable_path='./geckodriver')
        else:
            # fire_fox_options.add_argument('--headless')
            browser = selenium.webdriver.Firefox(options=fire_fox_options)
        browser.execute_script(f"location.href='{self.live_url}';")
        time.sleep(3)
        while True:
            try:
                unread_elements = browser.find_elements(By.XPATH,
                                                        "//div[@class='webcast-chatroom___unread-tips webcast-chatroom___unread']")
                if len(unread_elements) > 0:
                    unread_elements[0].click()
                    time.sleep(0.01)
                blank_elements = browser.find_elements(By.XPATH, "//div[@class='_1oBXuWfc']")
                blank_elements[0].click()
                msg_info = MessageInfo()
                page = browser.page_source
                etree = html.etree
                selector = etree.HTML(page)
                new_users = selector.xpath("//div[@class='webcast-chatroom___bottom-message']")
                for u in new_users:
                    user_sel = etree.HTML(etree.tostring(u, method='html'))
                    user = user_sel.xpath('//span[@class="tfObciRM"]/text()')
                    user = get_first_one_or_empty(user)
                    if len(user) < 1:
                        continue
                    msg_info.msg_type = 0
                    msg_info.msg = ''
                    msg_info.nick_name = user
                    if user in CommonInstance.users_dict:
                        continue
                    if len(CommonInstance.users_dict) > 5:
                        CommonInstance.users_dict = {}
                    CommonInstance.users_dict[user] = ''
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), user + '来了')

                    if user in CommonInstance.name_image_dic:
                        msg_info.image = CommonInstance.name_image_dic[user]
                        send_to_mq(msg_info)
                        continue
                    chat_elements = browser.find_elements(By.XPATH,
                                                          "//div[contains(@class,'webcast-chatroom___bottom-message')]//span[@class='tfObciRM']")
                    if len(chat_elements) == 0:
                        continue
                    chat_elements[0].click()
                    time.sleep(0.01)
                    set_user_image(browser, msg_info)
            except Exception as e:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'parse new user exception:', e)
