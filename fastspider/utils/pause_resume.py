# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/6/23 11:37
@Author     : lkkings
@FileName:  : pause_resume.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import asyncio
import threading
from abc import ABC
from typing import Any

import aiohttp

from fastspider.utils._signal import SignalManager


class AsyncPauseAbleTask(ABC, threading.Thread):
    def __init__(self, cfg: dict, loop: asyncio.AbstractEventLoop = None):
        super().__init__()
        self._cfg = cfg
        self._paused: bool = False
        self._running: bool = False
        self._status: int = 0  # 0/有更多，1/无更多，2/任务队列消费完全
        self._loop = loop or asyncio.get_event_loop()
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self._task_queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(cfg['thread_num'])
        connector = aiohttp.TCPConnector(ssl=cfg['ssl'],
                                         limit_per_host=cfg['limit_per_host'],
                                         limit=cfg['limit'])
        self._client = aiohttp.ClientSession(connector=connector)

    def pause(self):
        self._paused = True
        self._pause_event.set()

    def stop(self):
        self._running = False

    @property
    def running(self):
        return self._running

    @property
    def status(self):
        return self._status

    def set_status(self, status: int):
        self._status = status

    def unpause(self):
        self._paused = False
        self._pause_event.set()

    async def put_task(self, task: Any):
        raise NotImplementedError

    def remove_task(self, task_id: Any):
        raise NotImplementedError

    async def _task_handler(self, task_queue: asyncio.Queue):
        raise NotImplementedError

    async def _work(self):
        while self._running:
            if SignalManager.is_shutdown_signaled():
                break
            await self._pause_event.wait()
            await self._semaphore.acquire()
            await self._task_handler(self._task_queue)

    def run(self):
        self._running = True
        self._loop.run_until_complete(self._work())
