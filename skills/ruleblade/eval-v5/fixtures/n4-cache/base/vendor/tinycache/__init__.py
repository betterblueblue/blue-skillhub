"""tinycache：项目内置的极简内存缓存。"""
import time


class TinyCache:
    def __init__(self, *, ttl: float):
        self.ttl = ttl
        self._items = {}

    def fetch(self, key, loader):
        now = time.monotonic()
        hit = self._items.get(key)
        if hit is not None and now - hit[1] < self.ttl:
            return hit[0]
        value = loader()
        self._items[key] = (value, now)
        return value

    def drop(self, key):
        self._items.pop(key, None)
