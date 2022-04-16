# -*- coding: utf-8 -*-

def get_first_one_or_empty(msg) -> str:
    return str(msg[0]).strip() if len(msg) > 0 else ''
