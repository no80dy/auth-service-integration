import os
import sqlite3
import psycopg2

from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from postgres_worker import PostgresSaver
from sqlite_worker import SQLiteExtractor


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection)

    data = sqlite_extractor.extract_all_data()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    load_dotenv()

    POSTGRES_CONNECTION_PARAMS = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('PORT')
    }

    SQLITE_DATA_PATH = 'db.sqlite'

    with sqlite3.connect(SQLITE_DATA_PATH) as sqlite_conn, \
            psycopg2.connect(
                **POSTGRES_CONNECTION_PARAMS, cursor_factory=DictCursor
            ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
