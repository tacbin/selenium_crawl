# -*- coding: utf-8 -*-
import miraicle
from lxml import html
from selenium.webdriver.firefox.webdriver import WebDriver

from common.common_instantce import CommonInstance
from common_crawl import CommonCrawl


class ZhuBaJieCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.result = []

    def before_crawl(self, args, browser: WebDriver) -> WebDriver:
        self.urls = ["https://task.zbj.com/hall/list/h1"]
        self.file_location = 'zhu_ba_jie_crawl'
        self.is_save_img = False
        self.mode = 1
        return browser

    def parse(self, browser: WebDriver):
        print('zhu ba jie start crawl..')
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        tasks = selector.xpath('//div[@class="result-search-item"]')
        for task in tasks:
            sel = etree.HTML(etree.tostring(task, method='html'))
            title = sel.xpath('//div//h4/@title')
            title = title[0] if len(title) > 0 else ''
            title = title.replace('\n', '')

            detail = sel.xpath("//div[@class='pub-desc text-line-overflow-two']/text()")
            detail = detail[0] if len(detail) > 0 else ''
            detail = detail.replace('\n', '')

            money = sel.xpath('//div[@class="pub-handles"]//span/text()')
            money = money[0] if len(money) > 0 else ''
            money = money.replace('\n', '')

            url = sel.xpath('//h4//a/@href')
            url = url[0] if len(url) > 0 else ''
            url = url.replace('\n', '')
            url = url.replace('//', '')

            self.result.append(TaskResult(title, detail, money, url))
        print('zhu ba jie end crawl..')

    def custom_send(self):
        print('zhu ba jie start custom_send..')
        cache_result = CommonInstance.Redis_client.get('2840498397_zhu_ba_jie')
        cache_result = cache_result.decode("utf-8")
        first_one = ''
        for data in self.result:
            if first_one == '':
                first_one = data.url
            if data.url == cache_result:
                CommonInstance.Redis_client.set('2840498397_zhu_ba_jie', first_one)
                return
            txt = '商机来啦\n' \
                  '【%s】\n' \
                  '详情:%s\n' \
                  '价格:%s\n' \
                  '链接:%s' % (data.title, data.detail, data.money, data.url)
            CommonInstance.QQ_ROBOT.send_group_msg(group=461936572,
                                                   msg=[miraicle.Face.from_name('嘿嘿'), miraicle.Plain(txt),
                                                        miraicle.Face.from_name('鲸鱼')])
        CommonInstance.Redis_client.set('2840498397_zhu_ba_jie', first_one)


class TaskResult:
    def __init__(self, title, detail, money, url):
        self.title = title
        self.detail = detail
        self.money = money
        self.url = url
