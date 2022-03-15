# -*- coding: utf-8 -*-
from middleware.rabbit_mq import __init_rabbit_mq
from middleware.redis import __init_redis


def init_middleware():
    __init_rabbit_mq()
    __init_redis()
