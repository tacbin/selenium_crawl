# -*- coding: utf-8 -*-
import redis

from common.common_instantce import CommonInstance


def __init_redis():
    CommonInstance.Redis_client = redis.Redis(host='42.194.223.190', port=6379, password='tacbin@123')
