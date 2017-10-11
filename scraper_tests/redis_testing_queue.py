import redis

from .models import ProductPageUrl, Product, Review, Project

cache = redis.Redis(
            host='localhost',
            port=6379
        )

def set_redis_queue(ppu_id, source):
    cache.set(source, ppu_id)

def get_redis_queue(source):
    return int(cache.get(source))



