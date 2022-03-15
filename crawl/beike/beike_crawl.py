# -*- coding: utf-8 -*-
import re
import time
from typing import List

import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


class BeiKeCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.next_urls = []

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = ["https://sz.ke.com/ershoufang/co32/"]
        for url in self.urls:
            self.result_map[url] = []
        self.mode = 1
        self.file_location = 'bei_ke_crawl'
        self.is_save_img = False
        return browser

    def parse(self, browser: WebDriver):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'bei ke parse start crawl..',
              browser.current_url)
        if browser.current_url in self.urls:
            self.__list_strategy(browser)
        else:
            self.__detail_strategy(browser)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'bei ke parse end crawl..', browser.current_url)

    def __list_strategy(self, browser):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'bei ke list_strategy start crawl..',
              browser.current_url)
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        cards = selector.xpath("//ul[@class='sellListContent']//li[@class='clear']")
        for card in cards:
            sel = etree.HTML(etree.tostring(card, method='html'))
            title = sel.xpath('//a[contains(@class,"VIEWDATA")]/@title')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            url = sel.xpath('//a[contains(@class,"VIEWDATA")]/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            if CommonInstance.Redis_client.get(url) is not None:
                continue
            self.next_urls.append(url)

            community = sel.xpath('//div[@class="positionInfo"]//a/text()')
            community = community[0] if len(community) > 0 else ''
            community = community.replace('\n', '')

            house_info = sel.xpath('//div[@class="houseInfo"]')
            house_info = etree.tostring(house_info[0], encoding='utf-8',
                                        method='html')
            dr = re.compile(r'<[^>]+>', re.S)
            dd = dr.sub('', house_info.decode('utf-8'))
            dd = dd.replace('\n', '')
            house_info = dd.replace(' ', '')

            tag = etree.tostring(sel.xpath('//div[@class="tag"]')[0], encoding='utf-8',
                                 method='html')
            dr = re.compile(r'<[^>]+>', re.S)
            dd = dr.sub('', tag.decode('utf-8'))
            dd = dd.replace('\n', '')
            tag = dd.replace(' ', '')

            price = sel.xpath('//div[contains(@class,"totalPrice")]')
            price = etree.tostring(price[0], encoding='utf-8',
                                   method='html')
            dr = re.compile(r'<[^>]+>', re.S)
            dd = dr.sub('', price.decode('utf-8'))
            dd = dd.replace('\n', '')
            price = dd.replace(' ', '')
            self.result_map[browser.current_url].append(BeiKeResult(title, url, house_info, price, tag, community))
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'bei ke list_strategy end crawl..',
              browser.current_url)

    def __detail_strategy(self, browser):
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        detail = etree.tostring(selector.xpath("//div[@class='areaName']//span[@class='info']")[0], encoding='utf-8',
                                method='html')
        dr = re.compile(r'<[^>]+>', re.S)
        dd = dr.sub('', detail.decode('utf-8'))
        dd = dd.replace('\n', '')
        dd = dd.replace(' ', '')
        for url in self.urls:
            for item in self.result_map[url]:
                if item.url == browser.current_url:
                    item.area = dd

    def get_next_urls(self, browser: WebDriver) -> List[str]:
        return self.next_urls

    def custom_send(self):
        for url in self.result_map:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'wei ke start custom_send..', url)
            for data in self.result_map[url]:
                txt = '新房源\n' \
                      '【%s】\n' \
                      '区域:%s %s\n' \
                      '房子信息:%s\n' \
                      '价格:%s\n' \
                      '标签:%s\n' \
                      '链接:%s' % (data.title, data.area, data.community, data.house_info, data.price, data.tag, data.url)
                CommonInstance.QQ_ROBOT.send_group_msg(group=461936572,
                                                       msg=[miraicle.Face.from_name('嘿嘿'), miraicle.Plain(txt),
                                                            miraicle.Face.from_name('鲸鱼')])
                CommonInstance.Redis_client.set(data.url, '')


class BeiKeResult:
    def __init__(self, title, url, house_info, price, tag, community):
        self.title = title
        self.url = url
        self.community = community
        self.house_info = house_info
        self.price = price
        self.tag = tag
        self.area = ''
