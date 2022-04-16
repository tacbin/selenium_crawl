# -*- coding: utf-8 -*-
import json
import re
import time
from typing import List

import miraicle
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common.utils import get_first_one_or_empty

from common_crawl import CommonCrawl


class DouYinLiveCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = ["https://live.douyin.com/619641072814"]
        self.mode = 1
        self.file_location = 'dou_yin_live_crawl'
        self.is_save_img = False
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'dou_yin_live_crawl parse start crawl..',
              browser.current_url)
        voices_dict = {}
        users_dict = {}
        name_image_dic = {}
        while True:
            msg_info = MessageInfo()
            try:
                page = browser.page_source
                etree = html.etree
                selector = etree.HTML(page)
                voices = selector.xpath(
                    "//div[@class='webcast-chatroom___items']//div[@class='webcast-chatroom___item webcast-chatroom___enter-done']")
                for v in voices:
                    sel = etree.HTML(etree.tostring(v, method='html'))
                    nick_name = sel.xpath('//span[@class="tfObciRM"]/text()')
                    msg = sel.xpath('//span[@class="webcast-chatroom___content-with-emoji-text"]/text()')

                    nick_name = get_first_one_or_empty(nick_name)
                    msg = get_first_one_or_empty(msg)

                    unique_key = nick_name + '-' + msg

                    if unique_key in voices_dict:
                        continue
                    if len(voices_dict) > 10000:
                        voices_dict = {}
                    voices_dict[unique_key] = ''
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), nick_name, msg)
                    msg_info.msg_type = 1
                    msg_info.msg = msg
                    if nick_name not in name_image_dic:
                        elements = browser.find_elements(By.XPATH, '//span[@class="tfObciRM"]')
                        if len(elements) == 0:
                            continue
                        elements[0].click()
                        time.sleep(0.3)
                        page = browser.page_source
                        elements = browser.find_elements(By.ID, "root")
                        elements[0].click()
                        selector = etree.HTML(page)
                        image = selector.xpath("//div[@class='p-0+JvaK nsOPFX+X']//img[@class='qCM610OQ']/@src")
                        name = selector.xpath("//div[@class='_7KeH6hPD']/text()")

                        image = get_first_one_or_empty(image)
                        name = get_first_one_or_empty(name)
                        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), '头像对应', image, name)
                        name_image_dic[name] = image
                    msg_info.image = name_image_dic[nick_name]
                    msg_info.nick_name = nick_name

                new_users = selector.xpath("//div[@class='webcast-chatroom___bottom-message']")
                for u in new_users:

                    user_sel = etree.HTML(etree.tostring(u, method='html'))
                    user = user_sel.xpath('//span[@class="tfObciRM"]/text()')

                    user = get_first_one_or_empty(user)
                    if len(user) < 1:
                        continue

                    msg_info.msg_type = 0
                    msg_info.nick_name = user
                    if user in users_dict:
                        continue
                    if len(users_dict) > 10:
                        users_dict = {}
                    users_dict[user] = ''
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), user + '来了')

                    if user in name_image_dic:
                        msg_info.image = name_image_dic[user]
                        continue
                    elements = browser.find_elements(By.XPATH,
                                                     "//div[@class='webcast-chatroom___bottom-message']//span[@class='tfObciRM']")
                    if len(elements) == 0:
                        continue
                    elements[0].click()
                    time.sleep(0.5)
                    page = browser.page_source
                    elements = browser.find_elements(By.ID, "root")
                    elements[0].click()
                    time.sleep(0.1)

                    selector = etree.HTML(page)
                    image = selector.xpath("//div[@class='p-0+JvaK nsOPFX+X']//img[@class='qCM610OQ']/@src")
                    name = selector.xpath("//div[@class='_7KeH6hPD']/text()")

                    image = get_first_one_or_empty(image)
                    name = get_first_one_or_empty(name)
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), '头像对应', image, name)
                    name_image_dic[name] = image
                    msg_info.image = name_image_dic[user]
            except Exception as e:
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'dou_yin crawl exception:', e)
            finally:
                try:
                    if msg_info.nick_name is None:
                        return
                    self.channel.basic_publish(exchange="", routing_key="dou-yin-queue",
                                               body=json.dumps(msg_info.__dict__))
                except Exception as e:
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'send mq exception:', e)


class MessageInfo:
    def __init__(self):
        self.nick_name = ''
        # 0是加入，1是发消息
        self.msg_type = 0
        self.msg = ''
        self.image = ''
