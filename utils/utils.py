# -*- coding: utf-8 -*-
import re
import time


def get_first_one_or_empty(msg) -> str:
    return str(msg[0]).strip().split('：')[0] if len(msg) > 0 else ''


def get_current_time():
    t = time.time()
    return int(round(t))


def safeFilename(filename, replace=''):
    return re.sub(re.compile(
        '[/\\\:*?"<>|]')
        , replace,
        filename
    )