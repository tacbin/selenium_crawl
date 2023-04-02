# -*- coding: utf-8 -*-


from crawl.douyin.douyin_live_msg import DouYinMsgLiveCrawl

if __name__ == '__main__':
    wl = DouYinMsgLiveCrawl('https://live.douyin.com/574902600741')
    wl.run()
    # import requests
    #
    # url = "http://localhost:8080/live"
    # payload = "{\"message\":\"%s\",\"appId\":\"xaa\",\"token\":\"fff\",\"timestamp\":1111}" % "hello"
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
