# -*- coding: utf-8 -*-
from redis import Redis


class CommonInstance:
    Redis_client: Redis = None
    App_IS_LOCKED = False

    voices_dict = {}
    users_dict = {}
    name_image_dic = {}
