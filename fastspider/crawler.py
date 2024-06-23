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
import math
import os.path
import pickle
import sys
import threading
import time
import traceback
from asyncio import BaseEventLoop, AbstractEventLoop

from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod, abstractclassmethod
from typing import List, Tuple, Dict, Union, AsyncGenerator

import aiohttp
from yarl import URL

from fastspider.downloader import Downloader
from fastspider.items import Item, UniqueItem
from fastspider.http import Request, Response
from fastspider.logger import logger
from fastspider.exceptions import NotAsyncMethodError, MethodReturnError, APIError, ClassTypeError, Error
from fastspider.middleware import RedisManager
from fastspider.middleware.redis import BloomFilter
from fastspider.monitor import Monitor
from fastspider.storage import get_storage, BaseStorage
from fastspider.utils._trackref import object_ref
from fastspider.utils.common import false_empty_afunc
from fastspider.utils.pause_resume import AsyncPauseAbleTask
from fastspider.utils.reflection_utils import get_method_return_type
from fastspider.config import config


class CrawlerTask(object_ref):
    task_id: int
    do: Union[URL, str, Tuple]
    success: bool = False

    async def is_stopped(self, text: str) -> bool:
        return True

    @abstractclassmethod
    async def dedup(cls, item: UniqueItem, filter) -> bool:
        uid = str(item.get('id'))
        if filter.exists(uid):
            return True
        else:
            filter.add(uid)
            return False

    @abstractclassmethod
    async def load_tasks(cls, **params) -> AsyncGenerator[Union[URL, str, Tuple], None]:
        """
        该函数仅调用一次
        """
        yield []

    @abstractmethod
    async def request(self, task: Union[str, URL, Tuple], **params) -> Request:
        pass

    @abstractmethod
    async def parse(self, text: str, **params) -> AsyncGenerator[Dict, None]:
        yield None

    async def downloaded(self, request: Request, **params) -> AsyncGenerator[Dict, None]:
        pass


class Crawler(AsyncPauseAbleTask):
    def __init__(self, cfg: Dict, loop: AbstractEventLoop = None) -> None:
        cfg = cfg.get('crawler', {}).copy()
        super().__init__(cfg, loop)
        self._crawler_tasks = {}
        self._no_crawler_flag = []
        self._down_queue = asyncio.Queue()
        # self._executor = ThreadPoolExecutor(max_workers=cfg['parse_thread_num'])
        self.parse_thread_num = cfg['parse_thread_num']

    @property
    def down_queue(self):
        return self._down_queue

    async def put_task(self, task: Union[CrawlerTask, None]):
        if task and task.task_id in self._no_crawler_flag:
            self._no_crawler_flag.remove(task.task_id)
        await self._task_queue.put(task)
        if not task:
            self.set_status(1)

    def remove_task(self, task: CrawlerTask):
        if task.task_id in self._crawler_tasks:
            _task = self._crawler_tasks[task.task_id]
            _task.cancel()
            del self._crawler_tasks[task.task_id]
        else:
            self._no_crawler_flag.append(task.task_id)

    async def _try_fetch(self, crawler_task: CrawlerTask):
        request: Request = await crawler_task.request(task=crawler_task.do)
        try:
            response: Response = await request(self._client, self._cfg['retries'])
            text = await response.r.text()
            crawler_task.success = True
            await self._down_queue.put((crawler_task, text))
            return text
        except Exception as e:
            logger.error(e)
            crawler_task.success = False
            await self._down_queue.put((crawler_task, None))
            return None

    async def _fetch(self, crawler_task: CrawlerTask):
        text = await self._try_fetch(crawler_task)
        while text and not crawler_task.is_stopped(text):
            text = await self._try_fetch(crawler_task)
        self._semaphore.release()
        if crawler_task.task_id in self._crawler_tasks:
            del self._crawler_tasks[crawler_task.task_id]
        if self._task_queue.empty() and self._status == 1:
            self.set_status(2)
        if len(self._crawler_tasks) == 0 and self._status == 2:
            # 如果当前没有在运行的任务且任务队列全部消费完成则可以判定任务结束
            self._running = False
            await self._down_queue.put((None, -1))
            self._task_queue.put_nowait(None)

    async def _task_handler(self, task_queue: asyncio.Queue):
        crawler_task: CrawlerTask = await task_queue.get()
        if not crawler_task or crawler_task.task_id in self._no_crawler_flag:
            return
        task = self._loop.create_task(self._fetch(crawler_task))
        self._crawler_tasks[crawler_task.task_id] = task
