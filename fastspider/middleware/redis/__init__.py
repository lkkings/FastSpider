import hashlib
import math
from typing import Dict

import redis
from fastspider.utils._singleton import Singleton


class RedisManager(metaclass=Singleton):
    def __init__(self, cfg: Dict):
        _redis_cfg = cfg.get('redis', {}).copy()
        self.redis_conn = redis.StrictRedis(**_redis_cfg)

    def create_bloom_filter(self, name, capacity, error_rate=0.001):
        return BloomFilter(self.redis_conn, name, capacity, error_rate)

    def create_queue(self, name):
        return NamedQueue(self.redis_conn, name)

    def create_list(self, name):
        return NamedList(self.redis_conn, name)


class BloomFilter:
    def __init__(self, redis_conn, name, capacity, error_rate=0.001):
        self.redis_conn = redis_conn
        self.name = name
        self.capacity = capacity
        self.error_rate = error_rate

        # Calculate optimal number of bits and hash functions
        self.num_bits = math.ceil(capacity * abs(math.log(error_rate)) / (math.log(2) ** 2))
        self.num_hashes = math.ceil(self.num_bits * math.log(2) / capacity)

        # Redis key names
        self.bit_array_key = f"{self.name}:bitarray"
        self.num_hashes_key = f"{self.name}:num_hashes"

        # Initialize the bit array in Redis if it doesn't exist
        if not self.redis_conn.exists(self.bit_array_key):
            self.redis_conn.setbit(self.bit_array_key, self.num_bits - 1, 0)
            self.redis_conn.set(self.num_hashes_key, self.num_hashes)

    def add(self, item):
        hashes = self._calculate_hashes(item)
        for hash_value in hashes:
            self.redis_conn.setbit(self.bit_array_key, hash_value % self.num_bits, 1)

    def exists(self, item):
        hashes = self._calculate_hashes(item)
        for hash_value in hashes:
            if not self.redis_conn.getbit(self.bit_array_key, hash_value % self.num_bits):
                return False
        return True

    def _calculate_hashes(self, item):
        hashes = []
        md5 = hashlib.md5()
        md5.update(item.encode('utf-8'))
        seed = int(md5.hexdigest(), 16)

        for i in range(self.num_hashes):
            hash_value = (seed + i) % self.num_bits
            hashes.append(hash_value)
        return hashes


class NamedQueue:
    def __init__(self, redis_conn, name):
        self.redis_conn = redis_conn
        self.name = name

    def enqueue(self, item):
        self.redis_conn.lpush(self.name, item)

    def dequeue(self):
        return self.redis_conn.rpop(self.name)

    def size(self):
        return self.redis_conn.llen(self.name)

    def exists(self):
        return self.redis_conn.exists(self.name)

    def is_empty(self):
        return self.size() == 0


class NamedList:
    def __init__(self, redis_conn, name):
        self.redis_conn = redis_conn
        self.name = name

    def append(self, item):
        self.redis_conn.rpush(self.name, item)

    def prepend(self, item):
        self.redis_conn.lpush(self.name, item)

    def get(self, index):
        return self.redis_conn.lindex(self.name, index)

    def remove(self, item):
        self.redis_conn.lrem(self.name, 0, item)

    def size(self):
        return self.redis_conn.llen(self.name)

    def is_empty(self):
        return self.size() == 0

    def exists(self):
        return self.redis_conn.exists(self.name)

    def all(self):
        return self.redis_conn.lrange(self.name, 0, -1)
