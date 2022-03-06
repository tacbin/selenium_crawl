# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver

from common_crawl import CommonCrawl


class HokCrawl(CommonCrawl):
    def before_crawl(self, args):
        self.mode = 0
        self.file_location = 'hok_crawl'
        self.urls = ['https://pvp.qq.com/',
                     'https://pvp.ingame.qq.com/php/ingame/smoba/get_valuable_book.php?partition=1119&roleid=90876401&area=1&physicalID=1&algorithm=v2&version=2.14.6a&timestamp=1493112232746&appid=1104466820&sig=11a92c24e8f0d1fc74e31bb8c5203a09&encode=2&msdkEncodeParam=E5CB3C064B7A772867B1B552594434FCA26621A002CCB5AF47407E70297E2D6EE7962AC5C4D05234943B0144EDFBDCC4C2A285820C8983E5DE4E22B38EF167CCCA62220D5B3FF8BF83283431B8FF17FB790EDAA0932201873DEC7556F3CFF3AD325B51D6FF5A451618921BA48FF6818B53191FA3C7ED56E51021350FDC66A01CB44BB53178F3C501%20&game=smoba&start=1&num=20&ordertype=1&filter=0&grade=-1&herotype=1&matchtype=3&heroid=141',
                     'https://pvp.ingame.qq.com/php/ingame/smoba/top_heros.php?partition=1119&roleid=90876401&area=1&physicalID=1&algorithm=v2&version=2.14.6a&timestamp=1493112232746&appid=1104466820&sig=11a92c24e8f0d1fc74e31bb8c5203a09&encode=2&msdkEncodeParam=E5CB3C064B7A772867B1B552594434FCA26621A002CCB5AF47407E70297E2D6EE7962AC5C4D05234943B0144EDFBDCC4C2A285820C8983E5DE4E22B38EF167CCCA62220D5B3FF8BF83283431B8FF17FB790EDAA0932201873DEC7556F3CFF3AD325B51D6FF5A451618921BA48FF6818B53191FA3C7ED56E51021350FDC66A01CB44BB53178F3C501&game=smoba&start=1&num=20&ordertype=1&filter=0&grade=-1&herotype=0&matchtype=2',
                     'https://pvp.qq.com/web201605/js/herolist.json'
                     ]

    def parse(self, browser: WebDriver):
        print(browser.page_source)

    def before_send_email(self):
        pass
