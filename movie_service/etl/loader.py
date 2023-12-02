import json
import os

import requests
from requests.exceptions import RequestException

from helper import logger


class ElasticsearchLoader():
    """Клас для загрузки данных в Elasticsearch."""

    def __init__(self, es_url: str, schema: str):
        self.es_url = es_url
        if schema in ('genres', 'persons'):
            self.schema = schema
        else:
            raise ValueError(
                f'{self.__class__.__name__}: Unknown schema name: {schema}')

    def check_es_schema_exist(self) -> None:
        """Метод проверки существования/создания схемы в Elasticsearch."""
        if self.schema == 'genres':
            r = requests.get(f'{self.es_url}/genres/_mapping')
        elif self.schema == 'persons':
            r = requests.get(f'{self.es_url}/persons/_mapping')

        if r.status_code != 200:
            try:
                es_schema_path = os.path.join(
                    os.path.dirname(__file__), f'config/es_schema_{self.schema}.json')
                es_schema = json.load(
                    open(es_schema_path, 'r'))

                requests.put(f'{self.es_url}/{self.schema}',
                             headers={'Content-Type': 'application/json'}, data=json.dumps(es_schema))
                logger.info(f'Elasticsearch schema {self.schema} is created')
            except Exception as e:
                logger.error(f'{self.__class__.__name__}: {e}')

    def save_data(self, batch_records: str) -> None:
        """Медод записи пачки записей в Elasticsearch."""
        try:
            r = requests.post(
                f'{self.es_url}/_bulk', headers={'Content-Type': 'application/json'}, data=batch_records.encode('utf-8'))

            response = json.loads(r.text)
            if response['errors'] == True:
                for item in response['items']:
                    if item['index']['status'] != 200:
                        logger.error(
                            f"status: {item['index']['status']}, error_type: {item['index']['error']['type']}, film_id: {item['index']['_id']}")
                raise RequestException('mapper_parsing_exception')
        except Exception as e:
            logger.error(f'{self.__class__.__name__}: {e}')
            raise e
