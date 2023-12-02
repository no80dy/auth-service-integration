from db.redis import RedisCache


cache: RedisCache | None = None


async def get_cache() -> RedisCache:
    return cache
