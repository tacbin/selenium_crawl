# -*- coding: utf-8 -*-
# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
import json

import pika as pika

import crawl_mapping
from common_crawl import CommonCrawl


def msg_consumer(ch, method, properties, data_bytes):
    try:
        msg = data_bytes.decode()
        print('get msg:', msg)
        msg_dto = json.loads(msg)
        msg_type = msg_dto['type']
        msg_args = msg_dto['args']
        crawl = crawl_mapping.obj_mapping[msg_type]
        if isinstance(crawl, CommonCrawl):
            crawl.run(msg_args)
        else:
            print(crawl, 'does not implement CommonCrawl')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    credentials = pika.PlainCredentials('guest', 'tacbin@123')
    connection = pika.BlockingConnection(pika.ConnectionParameters('42.194.223.190', 5672, '/', credentials))
    channel = connection.channel()
    channel.basic_consume('selenium-crawl-queue',  # 队列名
                          msg_consumer,  # 回调函数
                          consumer_tag="selenium_crawl_consumer",
                          auto_ack=True
                          )
    print("start")
    channel.start_consuming()
