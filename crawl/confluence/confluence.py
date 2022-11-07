# -*- coding: utf-8 -*-
import json
import platform
import threading
import time

import miraicle
import selenium
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common.qq_robot import QQRobot
from common.utils import get_first_one_or_empty
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


# 先获取全部url。形成url树。每个url进行点击下载。叶子节点不再建文件夹。
class ConfluenceCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []
        self.tree = None
        self.file_name = ''
        self.url_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.next_urls = []
        self.urls = [
            "https://confluence.shopee.io/pages/viewpage.action?pageId=877396414"]
        for url in self.urls:
            self.result_map[url] = []
        self.file_location = 'confluence_crawl'
        self.is_save_img = True
        self.mode = 1
        self.build_tree(browser)
        return browser

    def build_tree(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ConfluenceCrawl start crawl..',
              browser.current_url)
        noted = False
        while "https://confluence.shopee.io/pages/" not in browser.current_url:
            if not noted:
                print("请登录后操作..")
                noted = True
            time.sleep(1)
        time.sleep(5)
        page_source = browser.page_source
        print("登录成功..")
        etree = html.etree
        selector = etree.HTML(page_source)
        pages = selector.xpath('//a')

        # 挑选出/pages/的前缀所有页面
        root = ConfluenceTree("root", browser.current_url, None)
        for p in pages:
            title = p.text
            url = p.get('href')
            if url is not None and url.startswith("/pages/viewpage.action?pageId") and not url.endswith(
                    'showComments=true&showCommentArea=true#addcomment'):
                url = 'https://confluence.shopee.io' + url
                node = ConfluenceTree(title, url, root)
                self.url_map[url] = node
                root.children.append(node)
                print(url)
                self.urls.append(url)
        self.recursive_search(root, browser, self.url_map)
        print(root)
        self.tree = root

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ConfluenceCrawl start crawl..',
              browser.current_url)
        self.file_name = self.url_map[browser.current_url].name
        pass

    def get_file_name(self):
        return self.file_name

    def recursive_search(self, root, browser: WebDriver, url_map):
        # 递归子页面
        for c in root.children:  # type:ConfluenceTree
            time.sleep(5)
            # 点击子页面
            browser.execute_script(f"location.href='{c.url}';")
            # 获取所有新的url
            page_source = browser.page_source
            etree = html.etree
            selector = etree.HTML(page_source)
            pages = selector.xpath('//a')
            for p in pages:
                title = p.text
                url = p.get('href')  # type:str
                if url is not None and url.startswith("/pages/viewpage.action?pageId") and not url.endswith(
                        'showComments=true&showCommentArea=true#addcomment'):
                    url = 'https://confluence.shopee.io' + url
                    if url in url_map:
                        continue
                    url_map[url] = ''
                    print(url)
                    self.urls.append(url)
                    node = ConfluenceTree(title, url, root)
                    root.children.append(node)
                    self.recursive_search(node, browser, url_map)

    def custom_send(self):
        pass
        # for url in self.result_map:
        #     print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke start custom_send..', url)
        #     for data in self.result_map[url]:
        #         txt = '新的订单\n' \
        #               '%s\n' \
        #               '区服:%s\n' \
        #               '价格:%s\n' \
        #               '%s\n' \
        #               'http://m.Confluence.com/v-3.0.9-zh_CN-/dlmm/index.w?language=zh_CN&skin=&ttt=random6833130&p3704878=pp1435623&t=1647424588903#!main' % (
        #                   data.title, data.area, data.money, data.end_time)
        #         QQRobot.send_group_msg(461936572, [miraicle.Plain(txt)])
        #         key = data.title + data.area + data.end_time + data.money
        #         CommonInstance.Redis_client.set(key, '')

    # def __trim_ele(self, ele: str):
    #     ele = ele[0] if len(ele) > 0 else ''
    #     return ele.replace('\n', '')


class ConfluenceTree:
    def __init__(self, name, url, parent):
        self.name = name
        self.url = url
        self.parent = parent
        self.children = []
