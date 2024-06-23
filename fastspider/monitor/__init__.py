# -*- coding: utf-8 -*-
"""
@Description: 监控层
@Date       : 2024/6/15 16:02
@Author     : lkkings
@FileName:  : __init__.py.py
@Github     : https://github.com/lkkings
@Mail       : lkkings888@gmail.com
-------------------------------------------------
Change Log  :

"""
import threading
import time

from fastspider.logger import logger


class Monitor(threading.Thread):
    n: int = 0

    def __init__(self):
        super().__init__()
        self.total_urls = 0
        self.success_urls = 0
        self._last_success_urls = 0
        self.failed_urls = 0
        self._last_failed_urls = 0
        self.errors = []
        self.speed = 0

        self._running = False

    def stop(self):
        self._running = False

    def report(self):
        return f'[失败:{self.failed_urls} | 成功:{self.success_urls} | 任务总数:{self.n} | 总请求数:{self.total_urls} | 速度:{self.speed}/s ]'

    def reset(self):
        self.total_urls = 0
        self.failed_urls = 0
        self.success_urls = 0
        self.errors.clear()

    def update(self, success=True, error=None):
        self.total_urls += 1
        if success:
            self.success_urls += 1
        else:
            self.failed_urls += 1
            if error:
                self.errors.append(error)

    def run(self):
        self._running = True
        while self._running:
            self._last_success_urls = self.success_urls
            time.sleep(10)
            self.speed = (self.success_urls-self._last_success_urls) / 10
            logger.debug(self.report())


