# -*- coding: utf-8 -*-
import pika

__rabbit_mq_conn = None


def get_rabbit_mq_channel():
    global __rabbit_mq_conn
    if __rabbit_mq_conn.is_closed:
        __init_rabbit_mq()
    return __rabbit_mq_conn


def __init_rabbit_mq():
    credentials = pika.PlainCredentials('guest', 'tacbin@123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('42.194.223.190', 5672, '/', credentials, heartbeat=0))
    global __rabbit_mq_conn
    __rabbit_mq_conn = connection.channel()
