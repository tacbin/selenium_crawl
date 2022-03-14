# -*- coding: utf-8 -*-
import json
import os
from typing import List
from urllib import parse

from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from xpinyin import Pinyin

from common.email import EmailInfo, AttachInfo
from common_crawl import CommonCrawl
import pandas as pd
from io import StringIO


class BossCrawl(CommonCrawl):

    def __init__(self):
        super().__init__()
        self.result_map = {}
        self.key_word_map = {}

    def before_crawl(self, args, browser: WebDriver):
        for _, value in enumerate(args):
            for i in range(0, len(value)):
                url = 'https://www.zhipin.com/job_detail/?query=%s&city=101280600&source=8' % value[i]
                self.urls.append(url)
                self.key_word_map[value[i]] = i
        self.mode = 0
        self.file_location = 'boss_crawl'
        self.is_save_img = True
        return browser

    def parse(self, browser: WebDriver):
        page = browser.page_source
        etree = html.etree
        selector = etree.HTML(page)
        companies = selector.xpath('//*[@id="main"]/div/div/ul/li/div')
        for c in companies:
            sel = etree.HTML(etree.tostring(c, method='html'))
            title = sel.xpath('//span[@class="job-name"]/a/@title')
            title = title[0] if len(title) > 0 else ''
            job_area = sel.xpath('//span[@class="job-area"]/text()')
            job_area = job_area[0] if len(job_area) > 0 else ''
            company_name = sel.xpath('//h3[@class="name"]/a/text()')
            company_name = company_name[0] if len(company_name) > 0 else ''
            min_salary = sel.xpath('//span[@class="red"]/text()')[0].split('-')[0]
            max_salary = sel.xpath('//span[@class="red"]/text()')[0].split('-')[1].split('K')[0]
            experience = sel.xpath('//*[@class="job-limit clearfix"]/p/text()[1]')[0]
            degree = sel.xpath('//*[@class="job-limit clearfix"]/p/text()[2]')[0]
            ware_fare = sel.xpath('//div[@class="info-desc"]/text()')
            ware_fare = ware_fare if len(ware_fare) > 0 else ['']
            company_icon = sel.xpath('//img[@class="company-logo"]/@src')[0]
            skills = sel.xpath('//span[@class="tag-item"]/text()')
            company_status = sel.xpath('//div[@class="company-text"]/p/text()[1]')[0]
            company_size = company_status
            if len(sel.xpath('//div[@class="company-text"]/p/text()[2]')) > 0:
                company_size = sel.xpath('//div[@class="company-text"]/p/text()[2]')[0]
            job_detail = "https://www.zhipin.com" + sel.xpath('//div[@class="primary-box"]/@href')[0]
            obj_dict = {
                "岗位": title,
                "工作地": job_area,
                "公司名": company_name,
                "福利": ware_fare,
                "最低薪资": min_salary,
                "最高薪资": max_salary,
                "学历": degree,
                "经验": experience,
                # "company_icon": company_icon,
                "公司融资状态": company_status,
                "公司规模": company_size,
                "要求的技能": skills,
                "岗位详情": job_detail,
            }
            for key in self.key_word_map:
                if "=" + parse.quote(key) not in browser.current_url:
                    continue
                if key in self.result_map:
                    self.result_map[key].append(obj_dict)
                else:
                    self.result_map[key] = [obj_dict]

    def before_send(self):
        self.email_info = EmailInfo()
        self.email_info.subject = '请查收数据'
        self.email_info.content = '详情请查看附件'
        self.email_info.receivers = ['2840498397@qq.com', '1208559252@qq.com']
        dirs = self.get_file_path()
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        # gen excel
        for key in self.result_map:
            df_json = pd.read_json(StringIO(json.dumps(self.result_map[key])))
            excel_file_path = os.path.join(dirs, '%s.xlsx' % key)
            df_json.to_excel(excel_file_path)
            attach = AttachInfo()
            p = Pinyin()
            attach.file_name = p.get_pinyin('%s.xlsx' % key)
            self.email_info.content = self.email_info.content + key + "(" + attach.file_name + ");"
            attach.file_location = excel_file_path
            self.email_info.attaches.append(attach)
        # exception no data
        if len(self.email_info.attaches) == 0:
            self.email_info.receivers = ['2840498397@qq.com']
            self.email_info.content = 'get no data'
            for img_url in self.get_img_local_path():
                attach = AttachInfo()
                attach.file_location = img_url
                self.email_info.attaches.append(attach)

    def get_next_elements(self, browser: WebDriver) -> List[WebElement]:
        return browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
