# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/22 11:42
@Author     : lkkings
@FileName:  : engine.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
import pickle
from concurrent.futures import ThreadPoolExecutor

import aiohttp

from fastspider import Request
from fastspider.items import Item, UniqueItem
from fastspider.crawler import Crawler, CrawlerTask
from fastspider.downloader import Downloader
from fastspider.config import ConfigManager
from fastspider.exceptions import ClassTypeError
from fastspider.logger import logger
from fastspider.middleware import RedisManager
from fastspider.monitor import Monitor
from fastspider.storage import get_storage
from fastspider.utils._signal import SignalManager
from fastspider.utils.common import false_empty_afunc
from fastspider.utils.reflection_utils import get_method_return_type


class Spider:
    name: str

    def __init__(self, name: str, cfg_path: str = None) -> None:
        cfg = ConfigManager(cfg_path).get_config(name)

        self.name = name
        self.__cfg = cfg

        self.__running: bool = False

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self._loop = loop

        self._monitor = Monitor()
        self._filter = RedisManager(cfg).create_bloom_filter(f'{self.name}.down_item',
                                                             capacity=cfg['bloom_size'])
        self._storage = get_storage(cfg)
        self._downloader = Downloader(cfg, loop=loop)
        self._crawler = Crawler(cfg, loop=loop)

        self._Item = None
        self._CrawlerTask = None

        self._crawler_tasks = {}

    @property
    def monitor(self) -> Monitor:
        return self._monitor

    def task(self):
        def decorator(cls):
            if issubclass(cls, CrawlerTask):
                self._CrawlerTask = cls
            else:
                raise ClassTypeError(o=cls, message='task类型必须为fastspider.CrawlerTask的子类')

        return decorator

    @property
    def filter(self):
        return self._filter

    def item(self):
        def decorator(cls):

            if issubclass(cls, Item):
                self._Item = cls
            else:
                raise ClassTypeError(o=cls, message='item类型必须为fastspider.Item的子类')

        return decorator

    async def _rev(self):
        with ThreadPoolExecutor(max_workers=self._crawler.parse_thread_num) as executor:
            while self._crawler.running:
                crawler_task, text = await self._crawler.down_queue.get()
                crawler_task: CrawlerTask
                if not crawler_task:
                    logger.info('任务全部完成')
                    continue
                if crawler_task.success:
                    self._monitor.update(success=True)
                    executor.submit(crawler_task.parse, text)
                else:
                    self._monitor.update(success=False)
                    await self._crawler.put_task(crawler_task)

    async def _send(self):
        task_id = 0
        async for task in self._CrawlerTask.load_tasks():
            if SignalManager.is_shutdown_signaled():
                break
            task_id += 1
            crawler_task: CrawlerTask = self._CrawlerTask()
            crawler_task.task_id = task_id
            crawler_task.do = task
            await self._crawler.put_task(crawler_task)
            self._crawler_tasks[task_id] = crawler_task
        await self._crawler.put_task(None)

    async def _work(self):
        send_task = asyncio.create_task(self._send())
        rev_task = asyncio.create_task(self._rev())
        await asyncio.gather(send_task, rev_task)

    def _before_run_check_(self):
        assert self._Item is not None, '未检测出Item'
        assert self._CrawlerTask is not None, '未检测出CrawlerTask'
        if not issubclass(self._Item, UniqueItem):
            self._CrawlerTask.dedup = false_empty_afunc
        request_method = getattr(self._CrawlerTask, 'request')
        return_type = get_method_return_type(request_method)
        assert issubclass(return_type, Request), f'{self._CrawlerTask.__name__} request方法应该返回Request类型'

    def start(self):
        if self.__running:
            raise RuntimeError("引擎已经处于运行状态！")
        self._before_run_check_()
        self.__running = True
        signal = SignalManager()
        signal.register_shutdown_signal()
        self._storage.start()
        self._monitor.start()
        self._crawler.start()
        self._downloader.start()
        self._loop.run_until_complete(self._work())

    def stop(self):
        if self._storage:
            self._storage.stop()
        if self._monitor:
            self._monitor.stop()
        if self._crawler:
            self._crawler.stop()
        if self._downloader:
            self._downloader.stop()
        SignalManager().shutdown()
        logger.info(f'{self.name}脚本停止运行')


class CrawlerEngine:

    def __init__(self, crawler: "Crawler", ):
        self.crawler: "Crawler" = crawler
        self.downloader: "Downloader" = Downloader()
        self.running: bool = False
        self.paused: bool = False

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def stop(self):
        self.running = False
