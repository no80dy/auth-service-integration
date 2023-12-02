import time
import backoff
import requests
import sys

from redis import Redis
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.functional.logger import logger


HOST = 'redis'
PORT = 6379
BACKOFF_MAX_TIME = 60

if __name__ == '__main__':
    redis_client = Redis(host=HOST, port=PORT)

    @backoff.on_exception(backoff.expo, (requests.exceptions.Timeout,
                                         requests.exceptions.ConnectionError), max_time=BACKOFF_MAX_TIME)
    def check_redis_readiness():
        while True:
            if redis_client.ping():
                logger.info('Redis ping Ok')
                break
            time.sleep(1)

    try:
        check_redis_readiness()
    except ConnectionError:
        print('Redis is not available')
        raise ConnectionError
