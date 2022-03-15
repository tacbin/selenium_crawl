# -*- coding: utf-8 -*-
import json
import threading

import crawl_mapping
from common_crawl import CommonCrawl
from middleware.rabbit_mq import get_rabbit_mq_channel


def msg_consumer(ch, method, properties, data_bytes):
    try:
        msg = data_bytes.decode()
        print('get msg:', msg)
        msg_dto = json.loads(msg)
        msg_type = msg_dto['type']
        msg_args = msg_dto['args']
        crawl = crawl_mapping.crawl_factory(msg_type)
        if isinstance(crawl, CommonCrawl):
            crawl.run(msg_args)
        else:
            print(crawl, 'does not implement CommonCrawl')
    except Exception as e:
        print(e)


def api_msg_consumer(ch, method, properties, data_bytes):
    try:
        pass
    except Exception as e:
        print(e)


class MqThreadControl(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name

    def run(self):
        channel = get_rabbit_mq_channel()
        channel.basic_consume('selenium-crawl-queue',  # 队列名
                              msg_consumer,  # 回调函数
                              consumer_tag="selenium_crawl_consumer",
                              auto_ack=True
                              )
        print("MqThreadControl start")
        channel.start_consuming()
