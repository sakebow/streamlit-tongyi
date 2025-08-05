import os
import json
from dotenv import load_dotenv
from functools import lru_cache
from redis import Redis, ConnectionPool, RedisError

load_dotenv()
REDIS_ADDR = os.environ["REDIS_ADDR"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_PASS = os.environ["REDIS_PASS"]
TTL_TIMEOUT = 60 * 60

@lru_cache(maxsize=1)
def get_redis() -> Redis:
    pool = ConnectionPool(
        host=REDIS_ADDR,
        port=REDIS_PORT,
        password=REDIS_PASS,
        db=0,
        max_connections=100,
    )
    return Redis(connection_pool=pool)

def redis_set_cache(key: str, value: dict | str) -> None:
    rds = get_redis()
    encode_value = json.dumps(value, ensure_ascii=False)
    try:
        rds.set(
            name=key, value=encode_value,
            ex=TTL_TIMEOUT, nx=True
        )
    except RedisError as exc:
        print(f"there's something weird about redis: {exc}")
    except ConnectionError as exc:
        print(f"connection broken: {exc}")
    except TimeoutError as exc:
        print(f"failed shaking hands: {exc}")

def redis_get_cache(key: str):
    rds = get_redis()
    response: bytes = None
    try:
        # GETEX 一次性续命，要求 Redis 6.2+
        response = rds.getex(name=key, ex=TTL_TIMEOUT)
    except AttributeError:
        # 兼容老版本：先 GET 再 EXPIRE
        response = rds.get(key)
        if response is not None:
            rds.expire(key, TTL_TIMEOUT)
    finally:
        response = json.loads(response) if response else None
    return response

if __name__ == '__main__':
    redis_set_cache('name', 'runoob')
    response: bytes = redis_get_cache('name')
    print(response)