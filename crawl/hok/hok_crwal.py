# -*- coding: utf-8 -*-
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

from common_crawl import CommonCrawl


class HokCrawl(CommonCrawl):
    def __init__(self):
        super().__init__()
        self.cookies = []

    def before_crawl(self, args, browser: WebDriver):
        self.mode = 0
        self.file_location = 'hok_crawl'
        self.urls = ['https://pvp.qq.com/',
                     # 'https://pvp.ingame.qq.com/php/ingame/smoba/get_valuable_book.php?partition=1119&roleid=90876401&area=1&physicalID=1&algorithm=v2&version=2.14.6a&timestamp=1493112232746&appid=1104466820&sig=11a92c24e8f0d1fc74e31bb8c5203a09&encode=2&msdkEncodeParam=E5CB3C064B7A772867B1B552594434FCA26621A002CCB5AF47407E70297E2D6EE7962AC5C4D05234943B0144EDFBDCC4C2A285820C8983E5DE4E22B38EF167CCCA62220D5B3FF8BF83283431B8FF17FB790EDAA0932201873DEC7556F3CFF3AD325B51D6FF5A451618921BA48FF6818B53191FA3C7ED56E51021350FDC66A01CB44BB53178F3C501%20&game=smoba&start=1&num=20&ordertype=1&filter=0&grade=-1&herotype=1&matchtype=3&heroid=141',
                     # 'https://pvp.ingame.qq.com/php/ingame/smoba/top_heros.php?partition=1119&roleid=90876401&area=1&physicalID=1&algorithm=v2&version=2.14.6a&timestamp=1493112232746&appid=1104466820&sig=11a92c24e8f0d1fc74e31bb8c5203a09&encode=2&msdkEncodeParam=E5CB3C064B7A772867B1B552594434FCA26621A002CCB5AF47407E70297E2D6EE7962AC5C4D05234943B0144EDFBDCC4C2A285820C8983E5DE4E22B38EF167CCCA62220D5B3FF8BF83283431B8FF17FB790EDAA0932201873DEC7556F3CFF3AD325B51D6FF5A451618921BA48FF6818B53191FA3C7ED56E51021350FDC66A01CB44BB53178F3C501&game=smoba&start=1&num=20&ordertype=1&filter=0&grade=-1&herotype=0&matchtype=2',
                     # 'https://pvp.qq.com/web201605/js/herolist.json'
                     ]
        browser = EventFiringWebDriver(browser, EventListeners())
        return browser

    def parse(self, browser: WebDriver):
        print(browser.page_source)

    def before_send(self):
        pass


class EventListeners(AbstractEventListener):
    def before_navigate_to(self, url, driver):
        print("before_navigate_to %s" % url)

    def after_navigate_to(self, url, driver):
        for cookie in [{'name': 'eas_sid', 'value': 'R1u664g6m7M5u500v4c6l7Z4U6', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291046, 'sameSite': 'None'}, {'name': 'LW_uid', 'value': 'M1Z6E4Y6I7s5u5v0s4G7Z2d9H7', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'None'}, {'name': 'isHostDate', 'value': '19059', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'PTTuserFirstTime', 'value': '1646697600000', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'isOsSysDate', 'value': '19059', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'PTTosSysFirstTime', 'value': '1646697600000', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'isOsDate', 'value': '19059', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'PTTosFirstTime', 'value': '1646697600000', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'pgv_info', 'value': 'ssid=s1649200100', 'path': '/', 'domain': '.qq.com', 'secure': True, 'httpOnly': False, 'sameSite': 'None'}, {'name': 'pgv_pvid', 'value': '4774665100', 'path': '/', 'domain': '.qq.com', 'secure': True, 'httpOnly': False, 'expiry': 2147385600, 'sameSite': 'None'}, {'name': 'weekloop', 'value': '0-0-0-11', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291047, 'sameSite': 'Lax'}, {'name': 'eas_entry', 'value': 'https%3A%2F%2Fopen.weixin.qq.com%2F', 'path': '/', 'domain': 'pvp.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841459, 'sameSite': 'None'}, {'name': 'wxcode', 'value': '031BPt0008QprN1MrH200ThsVE0BPt02', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'openid', 'value': 'owanlsqe7oi-di_oBi9K1m7ihQBI', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'access_token', 'value': '54_R2IymbzR-h3NfU7AoqKzfPfSytti_xPdWJzr6iAnqFzYZ278HE79VM1hBidqCyF8nu2qX5iY4jW8_dZXuDLRgC-FJ_1OLZw8p2vSINoJvoY', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'iegams_refresh_token', 'value': '54_R2IymbzR-h3NfU7AoqKzfB3F68u0CTPfelAiRW3KDoI2xquL31M8ZYapFcRc0RDb5VeOehbtuLgoNnf6Bier9gNpX5xonjWr6_t1cj92YuY', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'acctype', 'value': 'wx', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'appid', 'value': 'wx95a3a4d7c627e07d', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1646841460, 'sameSite': 'None'}, {'name': 'LW_sid', 'value': 'q1L6q4n6n7Z5n5F0U6l0P3E5l0', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'expiry': 1678291060, 'sameSite': 'None'}, {'name': 'ts_last', 'value': 'pvp.qq.com/', 'path': '/', 'domain': '.pvp.qq.com', 'secure': True, 'httpOnly': False, 'expiry': 1646756860, 'sameSite': 'None'}, {'name': 'ts_uid', 'value': '3439834746', 'path': '/', 'domain': '.pvp.qq.com', 'secure': True, 'httpOnly': False, 'expiry': 1709827060, 'sameSite': 'None'}, {'name': 'pvpqqcomrouteLine', 'value': 'index_index', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'sameSite': 'Lax'}, {'name': 'PTTDate', 'value': '1646755060381', 'path': '/', 'domain': '.pvp.qq.com', 'secure': False, 'httpOnly': False, 'sameSite': 'Lax'}, {'name': 'IED_LOG_INFO2', 'value': 'userUin%3Dowanlsqe7oi-di_oBi9K1m7ihQBI%26uin%3Dowanlsqe7oi-di_oBi9K1m7ihQBI%26loginType%3Dwx%26logtype%3Dwx%26nickName%3D%26nickname%3D%26userLoginTime%3D1646755056', 'path': '/', 'domain': '.qq.com', 'secure': False, 'httpOnly': False, 'sameSite': 'None'}]:
            driver.add_cookie(cookie)
        driver.refresh()

    def before_close(self, driver):
        print("before_close")

    def after_close(self, driver):
        print("after_close")

    def before_quit(self, driver):
        print("before_quit")

    def after_quit(self, driver):
        print("after_quit")
