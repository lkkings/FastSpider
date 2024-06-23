# 代理池
import random
import threading
import time
import traceback
from typing import List

import requests

from fastspider.utils._singleton import Singleton


class ProxyManager(metaclass=Singleton):
    pool_url = 'https://servers.qunyindata.com/GetWDProxy?count=100'
    refresh_time = 60 * 1

    def __init__(self, base_url: str = 'https://www.baidu.com'):
        super().__init__()
        self.base_url = base_url
        self._last_refresh_time = -1
        self._proxy_pool = []
        self._running = False

    def init(self, base_url: str = 'https://www.baidu.com'):
        self.base_url = base_url
        self._proxy_pool = self.get_available_proxies()
        assert len(self._proxy_pool) > 0, '无可用代理'
        print()



    @property
    def random(self):
        if len(self._proxy_pool) == 0:
            return None
        return random.choice(list(self._proxy_pool))

    @property
    def proxy(self) -> str:
        if len(self._proxy_pool) == 0:
            return None
        return self._proxy_pool[0]

    def use_dynamic(self):
        _t = threading.Thread(target=self._t)
        self._running = True
        _t.start()

    def _t(self):
        while self._running:
            time.sleep(self.refresh_time)
            self._proxy_pool = self.get_available_proxies()

    def disable_dynamic(self):
        self._running = False

    def ping(self, proxy: str):
        try:
            pp = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            r = requests.get(url=self.base_url, proxies=pp, timeout=(2, 5))
            if r.status_code in [200, 404, 403]:
                print(f'{proxy} is ok!')
                return True
            return False
        except Exception as e:
            print(f'{proxy} is fail!')
            return False

    def get_available_proxies(self) -> List[str]:
        try:
            available_proxies = set()
            res = requests.get(self.pool_url,timeout=(2,5))
            r_json = res.json()
            if res.status_code == 200 and r_json['code'] == 200:
                proxies = r_json['results']
                for proxy in proxies:
                    if self.ping(proxy):
                        available_proxies.add(f'http://{proxy}')
            return list(available_proxies)
        except Exception as e:
            traceback.print_exc()
            return []
