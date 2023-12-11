import sys
import time
import backoff
import requests

from pathlib import Path
from elasticsearch import Elasticsearch

sys.path.append(str(Path(__file__).resolve().parents[3]))

from tests.settings import test_settings
from tests.logger import logger


BACKOFF_MAX_TIME = 100

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'{test_settings.ES_HOST}:{test_settings.ES_PORT}')

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_time=BACKOFF_MAX_TIME
    )
    def check_es_readiness():
        while True:
            if es_client.ping():
                logger.info('Elasticsearch ping Ok')
                break
            time.sleep(1)

    try:
        check_es_readiness()
    except ConnectionError:
        print('Elasticsearch is not available')
        raise ConnectionError
