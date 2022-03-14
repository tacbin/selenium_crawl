# -*- coding: utf-8 -*-
import miraicle
from redis import Redis


class CommonInstance:
    QQ_ROBOT: miraicle.Mirai = None
    Redis_client: Redis = None
