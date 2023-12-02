import json
import os
import time
from datetime import datetime

import psycopg2
import requests
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from helper import backoff, logger
from pydantic_classes import Settings
from state_storage import JsonFileStorage, State
from extractor import PostgresExtractor
from transformer import Transformer
from loader import ElasticsearchLoader


# Время между заспуском очередного etl процесса (секунды)
REFRESH = 10


def run_etl_pipeline(pg_conn: _connection, es_url: str, schema: str, state: str) -> None:
    """Функция синхронизации данных Postgres и Elasticsearch по определенной схеме."""
    extractor = PostgresExtractor(pg_conn, schema)
    transformer = Transformer(schema)
    loader = ElasticsearchLoader(es_url, schema)

    all_records = extractor.extract_data(state)

    loader.check_es_schema_exist()

    for batch_records in all_records:
        transformed_batch_records = transformer.transform_batch_records(
            batch_records)
        loader.save_data(transformed_batch_records)

    logger.info(f'All data {schema} is up to date')


def run_etl(pg_conn: _connection, es_url: str) -> None:
    """Основная функция переноса данных из Postgres в Elasticsearch."""

    # получить состояние (дату последнего обновления)
    state_value = state.get_state(key='last_update')
    if not state_value:
        state_value = datetime(1900, 1, 1).isoformat(
            sep=' ', timespec='microseconds')

    # Возможное новое состояние, если синхронизация будет успешна
    new_state_value = datetime.now().isoformat(sep=' ', timespec='microseconds')

    try:
        run_etl_pipeline(pg_conn, es_url, schema='genres', state=state_value)
        run_etl_pipeline(pg_conn, es_url, schema='persons', state=state_value)

        # Установить новое состояние
        state.set_state(key='last_update', value=new_state_value)
        logger.info(
            f'Synchronize is completed on {state.get_state("last_update")}')
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    # Переменные окружения для установления связи с Postgress и Elasticsearch
    settings = Settings()

    pg_dsn = {'dbname': settings.PG_DB_NAME, 'user': settings.PG_DB_USER,
              'password': settings.PG_DB_PASSWORD, 'host': settings.PG_DB_HOST, 'port': settings.PG_DB_PORT}

    es_url = f'http://{settings.ES_HOST}:{settings.ES_PORT}'

    # Настройка работы с состоянием
    state_storage_file_path = os.path.join(os.path.dirname(
        __file__), 'state_storage/state_storage.json')
    state_storage = JsonFileStorage(state_storage_file_path)
    state = State(state_storage)

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def check_connection_to_elasticsearch(es_url: str) -> None:
        """Функция проверки доступности базы данных Elasticsearch."""
        r = requests.get(es_url)
        if r.status_code == 200:
            logger.info('ElasticSearch is available')

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def make_connection_to_postgres(pg_dsn: dict) -> _connection:
        """Функция проверки доступности базы данных Postgres."""
        with psycopg2.connect(**pg_dsn, cursor_factory=DictCursor) as pg_conn:
            logger.info('Postgres is connected')
            return pg_conn

    # Запуск работы приложения
    while True:
        try:
            check_connection_to_elasticsearch(es_url)
            pg_conn = make_connection_to_postgres(pg_dsn)
            run_etl(pg_conn, es_url)
            pg_conn.close()
        except ConnectionError:
            logger.error(
                f'ETL process is interrupted. Retry in {REFRESH} sec.')
        finally:
            time.sleep(REFRESH)
