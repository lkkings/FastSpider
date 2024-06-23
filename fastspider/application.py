# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/15 16:26
@Author     : lkkings
@FileName:  : application.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from concurrent.futures import ProcessPoolExecutor
from typing import Dict

from fastspider.crawler import Crawler
from fastspider.logger import log_setup
from fastspider.utils._singleton import Singleton


class FastSpider(metaclass=Singleton):
    def __init__(self, **params):
        self.params: Dict = params
        self.__crawler_map: Dict[str, Crawler] = {}

    def register(self, crawler: Crawler) -> None:
        __name = crawler.__name__
        if __name in self.__crawler_map:
            raise KeyError(f"{__name} 已经存在！")
        self.__crawler_map[__name] = crawler

    def run(self):
        self.__crawler_map = dict(sorted(self.__crawler_map.items(), key=lambda item: item[1].priority))
        __crawler_processes = [_crawler.run for _crawler in self.__crawler_map.values()]
        with ProcessPoolExecutor(max_workers=len(self.__crawler_map)) as executor:
            results = [executor.submit(process) for process in __crawler_processes]
