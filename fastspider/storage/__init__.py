# -*- coding: utf-8 -*-
"""
@Description: 存储层
@Date       : 2024/6/15 16:08
@Author     : lkkings
@FileName:  : __init__.py.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from typing import Dict

from fastspider.storage.base_storage import BaseStorage
from fastspider.storage.mango import MangoDB

__all__ = ['MangoDB']


def get_storage(cfg: Dict) -> BaseStorage:
    cfg = cfg.get('storage', {}).copy()
    storage_type = cfg.get('type')
    del cfg['type']
    if storage_type == 'mongodb':
        return MangoDB(cfg)
    else:
        raise TypeError
