# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/16 16:09
@Author     : lkkings
@FileName:  : baidu.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
from typing import AsyncGenerator, List, Union

from yarl import URL

from fastspider import Crawler, CrawlerTask, Response, Item, Request
from fastspider.logger import logger

crawler = Crawler(name='百度爬虫')


@crawler.init(thread_num=100, max_core_num=1000)
@crawler.task(retries=3,priority=0)
class BaiduCrawler(CrawlerTask):

    def load_urls(self, **params) -> List[Union[URL, str]]:
        return []

    async def request(self, **params) -> Request:
        pass

    async def parse(self, response: Response, **params) -> AsyncGenerator[Item, None]:
        pass

logger.error('======================')
crawler.run()
