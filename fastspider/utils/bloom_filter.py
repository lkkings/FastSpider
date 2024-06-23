import math
import mmh3  # 需要安装 mmh3 库，可以通过 pip 安装


class BloomFilter:
    def __init__(self, capacity, error_rate=0.01):
        self.capacity = capacity
        self.error_rate = error_rate
        self.bit_array_size = self.calculate_bit_array_size()
        self.num_hashes = self.calculate_num_hashes()
        self.bit_array = [False] * self.bit_array_size

    def calculate_bit_array_size(self):
        m = -(self.capacity * math.log(self.error_rate)) / (math.log(2) ** 2)
        return int(m)

    def calculate_num_hashes(self):
        k = (self.bit_array_size / self.capacity) * math.log(2)
        return int(k)

    def add(self, item):
        for seed in range(self.num_hashes):
            index = mmh3.hash(item, seed) % self.bit_array_size
            self.bit_array[index] = True

    def contains(self, item):
        for seed in range(self.num_hashes):
            index = mmh3.hash(item, seed) % self.bit_array_size
            if not self.bit_array[index]:
                return False
        return True

    def clear(self):
        self.bit_array = [False] * self.bit_array_size

# 示例用法
if __name__ == "__main__":
    bloom_filter = BloomFilter(capacity=1000, error_rate=0.05)

    # 添加元素到布隆过滤器中
    bloom_filter.add("apple")
    bloom_filter.add("banana")
    bloom_filter.add("orange")

    # 检查元素是否存在
    print(bloom_filter.contains("apple"))  # True
    print(bloom_filter.contains("grape"))  # False (可能误判，但这里没有添加过)

    # 如果元素不在布隆过滤器中，contains 方法可能会误判为存在
    print(bloom_filter.contains("strawberry"))  # False，但可能会误判为 True
