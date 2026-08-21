import hashlib
import math


class BloomFilter:
    def __init__(self, n_items: int, false_positive_rate: float = 0.01):
        self.n_items = n_items
        self.p = false_positive_rate
        self.m = self._optimal_size(n_items, false_positive_rate)
        self.k = self._optimal_hash_count(self.m, n_items)
        self.bit_array = [0] * self.m
        self.items_added = 0

    @staticmethod
    def _optimal_size(n, p):
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(1, int(math.ceil(m)))

    @staticmethod
    def _optimal_hash_count(m, n):
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))

    def _base_hashes(self, item: str):
        item_bytes = item.encode("utf-8")
        h1 = int(hashlib.md5(item_bytes).hexdigest(), 16)
        h2 = int(hashlib.sha1(item_bytes).hexdigest(), 16)
        return h1, h2

    def _positions(self, item: str):
        h1, h2 = self._base_hashes(item)
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str):
        positions = self._positions(item)
        for pos in positions:
            self.bit_array[pos] = 1
        self.items_added += 1
        return positions  

    def might_contain(self, item: str) -> bool:
        return all(self.bit_array[pos] for pos in self._positions(item))

    def current_fill_ratio(self):
        return sum(self.bit_array) / self.m

    def estimated_fp_rate(self):
        fill = self.current_fill_ratio()
        return fill ** self.k

    def stats(self):
        return {
            "bit_array_size_m": self.m,
            "hash_count_k": self.k,
            "items_added": self.items_added,
            "fill_ratio": round(self.current_fill_ratio(), 4),
            "estimated_fp_rate": round(self.estimated_fp_rate(), 6),
            "designed_fp_rate": self.p,
        }


class CountingBloomFilter(BloomFilter):

    def __init__(self, n_items: int, false_positive_rate: float = 0.01):
        super().__init__(n_items, false_positive_rate)
        self.bit_array = [0] * self.m  

    def add(self, item: str):
        positions = self._positions(item)
        for pos in positions:
            self.bit_array[pos] += 1
        self.items_added += 1
        return positions

    def remove(self, item: str):
        if not self.might_contain(item):
            return False
        for pos in self._positions(item):
            if self.bit_array[pos] > 0:
                self.bit_array[pos] -= 1
        self.items_added -= 1
        return True

    def might_contain(self, item: str) -> bool:
        return all(self.bit_array[pos] > 0 for pos in self._positions(item))


if __name__ == "__main__":
    bf = BloomFilter(n_items=1000, false_positive_rate=0.01)
    bf.add("alice123")
    bf.add("bob_the_builder")
    print("alice123 ->", bf.might_contain("alice123"))
    print("charlie ->", bf.might_contain("charlie_new"))
    print(bf.stats())
