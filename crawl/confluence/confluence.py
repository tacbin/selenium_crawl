# -*- coding: utf-8 -*-
import time
from telnetlib import EC

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from common_crawl import CommonCrawl


# 先获取全部url。形成url树。每个url进行点击下载。叶子节点不再建文件夹。
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
            "https://confluence.shopee.io/display/SSCP/Shopee+Supply+Chain+-+FPM"]
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
        browser.execute_script(f"location.href='{self.urls[0]}';")
        while "https://confluence.shopee.io/pages/" not in browser.current_url:
            if not noted:
                print("请登录后操作..")
                noted = True
            time.sleep(1)
        time.sleep(5)
        print("登录成功..")
        # 挑选出/pages/的前缀所有页面
        root = ConfluenceTree("home", browser.current_url, None)
        self.recursive_search(root, browser, self.url_map)
        print(root)
        self.tree = root

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'ConfluenceCrawl start crawl..',
              browser.current_url)
        return

    def recursive_search(self, root, browser: WebDriver, url_map):
        # 点击当前页
        browser.execute_script(f"location.href='{root.url}';")
        time.sleep(5)
        self.save_img(browser, 0, root.name)
        eles = browser.find_elements(By.XPATH, "//a[contains(@id,'action-menu-link')]")
        if len(eles) != 0:
            time.sleep(1)
            eles[0].click()
            time.sleep(1)
        eles = browser.find_elements(By.XPATH, "//a[contains(@id,'action-export-pdf-link')]")
        if len(eles) != 0:
            time.sleep(1)
            eles[0].click()
            time.sleep(2)
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
                print(url)
                node = ConfluenceTree(title, url, root)
                root.children.append(node)
                self.recursive_search(node, browser, url_map)

    def custom_send(self):
        pass


class ConfluenceTree:
    def __init__(self, name, url, parent):
        self.name = name
        self.url = url
        self.parent = parent
        self.children = []
