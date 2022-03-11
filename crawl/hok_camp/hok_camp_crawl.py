# -*- coding: utf-8 -*-
import json

from common_api_crawl import CommonApiCrawl
import requests

from middleware.rabbit_mq import get_rabbit_mq_channel

hero_list = 'hero_list'
hero_detail = 'hero_detail'


class HokCampCrawl(CommonApiCrawl):
    def __init__(self):
        self.url_map = {
            hero_list: 'https://kohcamp.qq.com/hero/getdetailranklistbyid',
            hero_detail: 'https://ssl.kohsocialapp.qq.com:10001/game/getheropageinfo'
        }
        self.token = ''
        self.hero_info = {}
        self.channel = get_rabbit_mq_channel()

    def run(self, args):
        self.token = args[0]
        self.__hero_list()
        for hero_id in self.hero_info:
            self.__hero_detail(hero_id)

    def __gen_kohcamp_header(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI '
                          'MiniProgramEnv/Windows WindowsWechat',
            'ssoAppId': 'campMiniProgram',
            'ssoOpenId': 'ydxcxxyDChJLycA5fzBpMxSxOvdaa9To',
            'ssoBusinessId': 'mini',
            'ssoToken': self.token,
            'Accept': 'application/json, text/plain, */*',
            'noencrypt': '1',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-us,en',
            'Accept-Encrypt': '',
            'X-Client-Proto': 'https',
            'Content-Type': 'application/json',
        }

    def __gen_ssl_header(self) -> dict:
        return {
            'NOENCRYPT': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        }

    def __hero_list(self):
        data = {
            "rankId": None,
            "position": 0,
            "segment": 1
        }
        try:
            resp = requests.post(self.url_map[hero_list],
                                 json=data, headers=self.__gen_kohcamp_header())
            if resp.status_code != 200:
                return
            resp_data = json.loads(resp.text)
            print('data hero list,req:%s,resp%s' % (resp.request.body, resp_data))
            if int(resp_data['returnCode']) != 0:
                return
            for hero in resp_data['data']['list']:
                self.hero_info[hero['heroInfo']['heroId']] = hero['heroInfo']['heroName']
                msg_data = {
                    "msgType": "heroBaseInfo",
                    "baseInfoDto": {
                        "heroId": hero['heroInfo']['heroId'],
                        "heroName": hero['heroInfo']['heroName'],
                        "heroIcon": hero['heroInfo']['heroIcon'],
                    }
                }
                self.channel.basic_publish(exchange="", routing_key="hok-hero-queue", body=json.dumps(msg_data))
        except Exception as e:
            print(e)

    def __hero_detail(self, hero_id):
        try:
            data = {
                'cClientVersionCode': '9999999999',
                'cClientVersionName': '9.99.999',
                'gameId': '20001',
                'cGameId': '20001',
                'ssoOpenId': 'ydxcxxyDChJLycA5fzBpMxSxOvdaa9To',
                'ssoToken': self.token,
                'ssoAppId': 'campMiniProgram',
                'ssoBusinessId': 'mini',
                'userId': '417198608',
                'uniqueRoleId': '843489140',
                'heroId': hero_id
            }
            resp = requests.post(self.url_map[hero_detail],
                                 data=data, headers=self.__gen_ssl_header())
            if resp.status_code != 200:
                return
            resp_data = json.loads(resp.text)
            print('data hero detail,req:%s,resp%s' % (resp.request.body, resp_data))
            if int(resp_data['returnCode']) != 0:
                return

            msg_data = {
                "msgType": "heroDetailInfo",
                "detailInfoDto": {
                    "heroId": hero_id,
                    "heroName": self.hero_info[hero_id],
                    "blood": '',
                    'mag': '',
                    "phyAttack": '',
                    "speed": '',
                    "magAttack": '',
                    "psyDef": '',
                    "magDef": '',
                    "attackSpeed": '',
                    "critRate": '',
                    "critEffect": '',
                    "attackRange": '',
                    "bloodRecover": '',
                    "magRecover": '',
                    "level": 1,
                }
            }
            base_info = resp_data['data']['attrInfo']['base']
            attack_info = resp_data['data']['attrInfo']['attack']
            defence_info = resp_data['data']['attrInfo']['defence']
            detail = msg_data['detailInfoDto']
            for info in base_info:
                if info['name'] == '最大生命':
                    detail['blood'] = info['data']
                elif info['name'] == '最大法力':
                    detail['mag'] = info['data']
                elif info['name'] == '法术攻击':
                    detail['magAttack'] = info['data']
                elif info['name'] == '物理攻击':
                    detail['phyAttack'] = info['data']
                elif info['name'] == '物理防御':
                    detail['psyDef'] = info['data']
                elif info['name'] == '法术防御':
                    detail['magDef'] = info['data']
                else:
                    pass
            for info in attack_info:
                if info['name'] == '移速':
                    detail['speed'] = info['data']
                elif info['name'] == '攻速加成':
                    detail['attackSpeed'] = info['data']
                elif info['name'] == '暴击几率':
                    detail['critRate'] = info['data'].split('%')[0]
                elif info['name'] == '暴击效果':
                    detail['critEffect'] = info['data'].split('%')[0]
                elif info['name'] == '攻击范围':
                    detail['attackRange'] = info['data']
                else:
                    pass
            for info in defence_info:
                if info['name'] == '每五秒回血':
                    detail['bloodRecover'] = info['data']
                elif info['name'] == '每五秒回蓝':
                    detail['magRecover'] = info['data']
                else:
                    pass
            self.channel.basic_publish(exchange="", routing_key="hok-hero-queue", body=json.dumps(msg_data))

        except Exception as e:
            print(e)
