import psycopg2
import logging
import contextlib

from dataclasses import fields, astuple
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch


class PostgresSaver:
    """Класс для загрузки данных в PostgreSQL"""
    def __init__(self, connection: _connection):
        self.connection = connection

    def save_data(self, table_name, data, page_size=100):
        """Метод загрузки данных из таблицы PostgreSQL пакетами"""
        column_names = ', '.join([field_.name for field_ in fields(data[0])])
        placeholders = ', '.join(['%s']*len(fields(data[0])))
        query = (
                f'INSERT INTO content.{table_name} ({column_names}) '
                f'VALUES ({placeholders})'
                'ON CONFLICT (id) DO NOTHING'
            )
        data_values = [astuple(row) for row in data]

        try:
            with contextlib.closing(self.connection.cursor()) as cursor:
                execute_batch(cursor, query, data_values, page_size=page_size)
                self.connection.commit()
        except psycopg2.Error as pg_error:
            logging.error(f'PostgreSQL: {pg_error}')

    def save_all_data(self, data: dict):
        """Сохранение всех извлеченных данных"""
        for table_name, table_data in data.items():
            for batch_data in table_data:
                self.save_data(table_name, batch_data)
