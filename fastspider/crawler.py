# -*- coding: utf-8 -*-
"""
@Description: 爬虫类
@Date       : 2024/6/15 16:14
@Author     : lkkings
@FileName:  : crawler.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
import inspect
import math
import sys
import traceback

from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Union, AsyncGenerator

import aiohttp
from yarl import URL

from fastspider.items import Item
from fastspider.http import Request, Response
from fastspider.logger import logger
from fastspider.exceptions import NotAsyncMethodError, MethodReturnError, APIError, ClassTypeError
from fastspider.utils._trackref import object_ref


class CrawlerTask(object_ref):
    task_id: int  # 将成功的次数作为id
    url: Union[URL, str]

    def __int__(self, retries: int = 3):
        self._retries = retries

    @property
    def retries(self) -> int:
        return self._retries

    @abstractmethod
    def load_urls(self, **params) -> List[Union[URL, str]]:
        return []

    @abstractmethod
    async def request(self, **params) -> Request:
        pass

    @abstractmethod
    async def parse(self, response: Response, **params) -> AsyncGenerator[Item, None]:
        yield None


class Crawler:
    name: str

    def __init__(self, name: str, thread_num=5, max_core_num=5, priority=0) -> None:
        self.name = name
        self.__priority: int = priority
        self.__thread_num: int = thread_num
        self.__max_core_num: int = max_core_num
        self.__urls: List[Union[str, URL]] = []
        self.__crawler_task: Union[None, CrawlerTask] = None
        self.__items_temp_queue: asyncio.Queue = asyncio.Queue()

    @property
    def priority(self) -> int:
        return self.__priority

    @property
    def thread_num(self) -> int:
        return self.__thread_num

    @property
    def urls(self) -> List[str]:
        return self.__urls

    @property
    def core_num(self) -> int:
        return self.__thread_num

    def task(self, retries=3, priority=0):
        self.__priority = priority

        def decorator(cls):
            if issubclass(cls, CrawlerTask):
                _CrawlerTask: CrawlerTask = cls
                instance = _CrawlerTask(retries)
                self.__crawler_task = instance
                __urls = instance.load_urls()
                if not isinstance(__urls, List):
                    raise MethodReturnError(o=cls, message='load_urls返回类型应为List[str,URL]')
                self.__urls.extend(__urls)
            else:
                raise ClassTypeError(o=cls, message='类型必须为fastspider.CrawlerTask的子类')

        return decorator

    def init(self, thread_num: int = 5, max_core_num: int = 5):
        self.__thread_num = thread_num
        self.__max_core_num = max_core_num

        def decorator(o):
            pass

        return decorator

    async def _core(self, sem: asyncio.Semaphore, client: aiohttp.ClientSession) -> None:
        async with sem:
            if len(self.__urls) == 0:
                return
            __url = self.__urls.pop()
            self.__crawler_task.url = __url
            _exec_success_count = 0
            while True:
                try:
                    self.__crawler_task.task_id = _exec_success_count
                    __task = self.__crawler_task
                    __request: Request = await __task.request()
                    if not isinstance(__request, Request):
                        raise MethodReturnError(o=__task.request, message='返回类型应为fastspider.Request')
                    __response: Response = await __request(client=client, retries=__task.retries)
                    async for __item in __task.parse(__response):
                        if not isinstance(__item, Item):
                            raise MethodReturnError(o=__task.request, message='返回类型应为fastspider.Item')
                        await self.__items_temp_queue.put(__item)
                    _exec_success_count += 1
                except MethodReturnError as e:
                    logger.error(e)
                    sys.exit(0)
                except Exception as e:
                    logger.error(e)
                    traceback.print_exc()
                    break

    async def _worker(self):
        __sem = asyncio.Semaphore(self.__max_core_num)
        __n = math.ceil(len(self.__urls) / self.__thread_num)
        __client = aiohttp.ClientSession()
        __core_tasks = [asyncio.create_task(self._core(__sem, __client)) for _ in range(__n)]
        await asyncio.gather(*__core_tasks)
        await __client.close()

    def _run_event_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._worker())

    def run(self):
        __loops = [asyncio.new_event_loop() for _ in range(self.thread_num)]
        with ThreadPoolExecutor(max_workers=self.__thread_num) as executor:
            results = [executor.submit(self._run_event_loop, _loop) for _loop in __loops]
