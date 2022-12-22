# -*- coding: utf-8 -*-
import json
import time
import uuid

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


# 边获取url边下载
class ConfluenceCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []
        self.tree = None
        self.url_map = {}

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.next_urls = []
        self.urls = [
            "https://confluence.shopee.io/pages/viewpage.action?pageId=902020112"]
        for url in self.urls:
            self.result_map[url] = []
        self.file_location = 'confluence_crawl'
        self.is_save_img = True
        self.mode = -1
        self.build_tree(browser)
        return browser

    def build_tree(self, browser: WebDriver):
        browser.execute_script(f"location.href='{self.urls[0]}';")
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ConfluenceCrawl start crawl..',
              browser.current_url)
        noted = False
        # 获取cookie
        list_cookies = self.load_cookie(browser, 'confluence.json')
        browser.delete_all_cookies()
        for cookie in list_cookies:
            browser.add_cookie(cookie_dict=cookie)
        browser.refresh()
        while "https://confluence.shopee.io/pages/" not in browser.current_url:
            if not noted:
                print("请登录后操作..")
                noted = True
            time.sleep(1)
        time.sleep(5)
        print("登录成功..")
        # 挑选出/pages/的前缀所有页面
        root = load_tree()
        if root is None:
            root = ConfluenceTree("root", browser.current_url, uuid.uuid4().hex, -1)
        print('root init:', root)
        self.recursive_search(root, browser, self.url_map)
        print(root)
        self.tree = root

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ConfluenceCrawl start crawl parse..',
              browser.current_url)
        return

    def recursive_search(self, root, browser: WebDriver, url_map):
        try:
            opt_url = root.url.split("&", 2)[0]
            if CommonInstance.Redis_client.get(opt_url) is None:
                while "https://confluence.shopee.io/pages/" not in browser.current_url:
                    print("请登录后操作..")
                    time.sleep(1)
                # 点击当前页
                browser.execute_script(f"location.href='{root.url}';")
                time.sleep(2)
                self.save_cookie(browser,'confluence.json')
                self.save_img(browser, 0, root.name)
                time.sleep(8)
                eles = browser.find_elements(By.XPATH, "//a[contains(@id,'action-menu-link')]")
                if len(eles) != 0:
                    time.sleep(1)
                    eles[0].click()
                    time.sleep(3)
                eles = browser.find_elements(By.XPATH, "//a[contains(@id,'action-export-pdf-link')]")
                if len(eles) != 0:
                    time.sleep(1)
                    eles[0].click()
                    time.sleep(5)
                CommonInstance.Redis_client.set(opt_url, '')

        except Exception as e:
            print(e, root.url, root.name)
        # 获取所有新的url
        page_source = browser.page_source
        etree = html.etree
        selector = etree.HTML(page_source)
        pages = selector.xpath('//a')
        for p in pages:
            title = p.text
            url = p.get('href')  # type:str
            if title is None:
                continue
            if url is not None and url.startswith("/pages/viewpage.action?pageId") and not url.endswith(
                    'showComments=true&showCommentArea=true#addcomment'):
                url = 'https://confluence.shopee.io' + url
                if url in url_map:
                    continue
                url_map[url] = ''
                title += ' -> ' + url.split('pageId=', 2)[1].split('&', 2)[0]
                print(url + " " + title)
                with open("./confluence_crawl/1_file_name.txt", "a") as my_file:
                    my_file.write(url + " " + title + "\n")
                if '周报' in title or '日报' in title or '大促计划' in title:
                    continue
                node = ConfluenceTree(title, url, uuid.uuid4().hex, root.node_id)
                root.add_child(node)
        for c in root.children:
            self.recursive_search(c, browser, url_map)


class ConfluenceTree:
    def __init__(self, name, url, node_id, parent_id, is_new=True):
        self.node_id = node_id
        self.parent_id = parent_id
        self.name = name
        self.url = url
        self.parent = None
        self.children = []

        if is_new:
            inner_json = json.dumps(self.__dict__)
            with open("./confluence_crawl/tree.txt", "a") as my_file:
                my_file.write(inner_json + "\n")

    def add_child(self, node):
        node.parent = self
        self.children.append(node)


def handle(d):
    tree = ConfluenceTree(d['name'], d['url'], d['node_id'], d['parent_id'], False)
    tree.parent_id = d['parent_id']
    return tree


def load_tree():
    node_map = {}
    root = None
    with open("./confluence_crawl/tree.txt", "r+") as my_file:
        lines = my_file.readlines()
        for line in lines:
            if len(line) == 0:
                return root
            line = line.replace("\n", "")
            c = json.loads(line, object_hook=handle)  # type:ConfluenceTree
            node_map[c.node_id] = c
        for line in lines:
            line = line.replace("\n", "")
            c = json.loads(line, object_hook=handle)  # type:ConfluenceTree
            if c.parent_id in node_map:
                node_map[c.parent_id].add_child(c)
            else:
                root = c
    return root
