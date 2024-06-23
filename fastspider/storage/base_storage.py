import threading
import time
import traceback
from abc import ABC, abstractmethod
from typing import List

from fastspider import Item
from fastspider.logger import logger


class BaseStorage(ABC, threading.Thread):
    collection: str = ''

    def __init__(self):
        super().__init__()
        self._p = 0
        self._temp_size = 100
        self._temp_ = []
        self.running = False

    @abstractmethod
    def init(self):
        pass

    def add(self, item: Item):
        self._temp_.append(item)
        self._p += 1

    def stop(self):
        self.running = False
        if len(self._temp_) > 0:
            self.save()

    @abstractmethod
    def _save(self, items: List[Item]):
        raise NotImplemented

    def save(self):
        try:
            self._save(self._temp_)
            self._p = 0
            self._temp_.clear()
        except Exception as e:
            traceback.print_exc()
            logger.error(f'保存失败 {e}')

    def all(self):
        raise NotImplemented

    def run(self):
        self.init()
        self.running = True
        _start_time = time.time()
        while self.running:
            time.sleep(0.3)
            if self._p > self._temp_size:
                n = len(self._temp_)
                _end_time = time.time()
                logger.debug(f'{n}条 | 速度 {n / (_end_time - _start_time)}/s')
                self.save()
                _start_time = time.time()
