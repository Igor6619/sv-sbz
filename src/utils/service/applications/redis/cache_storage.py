import json
from uuid import uuid4
from dataclasses import dataclass
from redis.asyncio import Redis
from typing import Optional, Union
from ...setting import RedisSetting


class RedisCacheStorage:
    """Хранилище кеширования объектов"""

    @dataclass
    class CacheItem:
        loads: bool = False
        updated: bool = False
        deleted: bool = False
        source: Optional[str] = None
        data: Optional[Union[list, dict]] = None

    def __init__(self, id: str, redis_setting: RedisSetting):
        self.id = id
        self.session = str(uuid4())
        self.r = Redis(
            host=redis_setting.host,
            port=redis_setting.port,
            db=redis_setting.db,
        )

        self._cache = dict[str, RedisCacheStorage.CacheItem]()
        self._load_keys = set[str]()
        self._has_load_all_keys = False
        self._loaded_keys = set[str]()
        self._has_loaded_all_keys = False
        self._aenter_index = 0

    async def get(self, key) -> Union[list, dict, None]:
        if not self._has_loaded_all_keys and key not in self._loaded_keys:
            await self.load_keys(key)

        if self._has_load_all_keys or len(self._load_keys) > 0:
            await self._cache_load()

        item = self._cache.get(key, None)
        if item is not None:
            if not item.loads and item.source is not None:
                item.data = json.loads(item.source)
            return item.data
        return None

    async def set(self, key: str = None, value: any = None, values: dict = None):
        if key is not None:
            item = self._cache.get(key, None)
            if item is not None:
                item.data = value
                item.loads = True
                item.updated = True
            else:
                self._cache[key] = RedisCacheStorage.CacheItem(
                    loads=True,
                    updated=True,
                    deleted=False,
                    data=value,
                )
        elif values is not None:
            for k, v in values.items():
                await self.set(k, v)

    async def delete(self, *keys):
        for key in keys:
            if key in self._cache:
                self._cache[key].deleted = True
            else:
                self._cache[key] = RedisCacheStorage.CacheItem(deleted=True)

    async def keys(self) -> list[str]:
        if not self._has_loaded_all_keys:
            self._has_load_all_keys = True
            await self._cache_load()

        return list(self._cache.keys())

    async def values(self) -> list[list, dict, None]:
        if not self._has_loaded_all_keys:
            self._has_load_all_keys = True
            await self._cache_load()

        for item in [
            item
            for item in self._cache.values()
            if not item.loads and item.source is not None
        ]:
            item.data = json.loads(item.source)
            item.loads = True

        return [item.data for item in self._cache.values()]

    async def items(self) -> list[tuple[str, Union[list, dict]]]:
        return zip(await self.keys(), await self.values())

    async def load_all(self):
        if not self._has_loaded_all_keys:
            self._has_load_all_keys = True

    async def load_keys(self, *keys):
        for key in keys:
            if key not in self._loaded_keys:
                self._load_keys.add(key)

    async def commit(self):
        updated = {key: value for key, value in self._cache.items() if value.updated}
        deleted = [key for key, value in self._cache.items() if value.deleted]

        if len(updated) > 0:
            values = {
                key: json.dumps(value.data, ensure_ascii=False)
                for key, value in updated.items()
                if value.data is not None
            }
            for key, value in values.items():
                await self.r.hset(self.id, key, value)
            # await self.r.hsetex(self.id, mapping=values)

            for v in updated.values():
                v.updated = False

        if len(deleted) > 0:
            await self.r.hdel(self.id, *deleted)

            for k in deleted:
                del self._cache[k]

    async def avalaible(self):
        return await self.r.exists(self.id)

    async def dispose(self):
        await self.r.delete(self.id)

    async def _cache_load(self):
        if self._has_load_all_keys:
            for key, value in (await self.r.hgetall(self.id)).items():
                key_str = key.decode(encoding="utf-8")
                if key_str in self._cache:
                    item = self._cache[key_str]
                    if item.updated or item.deleted:
                        continue

                self._cache[key_str] = RedisCacheStorage.CacheItem(
                    loads=False, updated=False, deleted=False, source=value
                )

            self._has_load_all_keys = False
            self._has_loaded_all_keys = True
            self._load_keys = set()

        elif len(self._load_keys) > 0:
            for key, value in zip(
                self._load_keys,
                await self.r.hmget(self.id, self._load_keys),
            ):
                if key in self._cache:
                    item = self._cache[key]
                    if item.updated or item.deleted:
                        continue

                self._cache[key] = RedisCacheStorage.CacheItem(
                    loads=False, updated=False, deleted=False, source=value
                )
            self._loaded_keys.update(self._load_keys)
            self._load_keys = set()

    async def __aenter__(self):
        self._aenter_index += 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._aenter_index -= 1
        if self._aenter_index <= 0:
            await self.commit()


__all__ = ["RedisCacheStorage"]
