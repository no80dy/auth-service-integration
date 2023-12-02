import os
import pytest
import sqlite3
import psycopg2
import contextlib

from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from .pydantic_models import (
    Person,
    Genre,
    Filmwork,
    PersonFilmwork,
    GenreFilmwork
)

load_dotenv()

POSTGRES_CONNECTION_PARAMS = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT')
}

SQLITE_DATA_PATH = '../../sqlite_to_postgres/db.sqlite'


@pytest.fixture(scope='module')
def sqlite_test_connection():
    """
    SQLite connection fixture

    Yields:
        sqlite3.Connection: Connection to SQLite.
    """
    connection = sqlite3.connect(SQLITE_DATA_PATH)
    connection.row_factory = sqlite3.Row

    yield connection
    print('SQLite closed.')
    connection.close()


@pytest.fixture(scope='module')
def postgres_test_connection():
    """
    PostgreSQL connection fixture

    Yields:
        _connection: Connection to PostgreSQL.
    """
    connection = psycopg2.connect(**POSTGRES_CONNECTION_PARAMS)

    yield connection
    connection.close()


def test_data_migration_consistency(
    sqlite_test_connection: sqlite3.Connection,
    postgres_test_connection: _connection
):
    """
    Method to check the consistency of data counts between SQLite
    and PostgreSQL tables.

    Args:
        sqlite_test_connection (sqlite3.Connection): SQLite connection fixture.
        postgres_test_connection (_connection): PostgreSQL connection fixture.

    Asserts:
        int: count between SQLite table and PostgreSQL table.
    """
    tables_to_check = [
        'person',
        'genre',
        'film_work',
        'person_film_work',
        'genre_film_work',
    ]

    for table_name in tables_to_check:
        try:
            with contextlib.closing(sqlite_test_connection.cursor()) \
                    as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name};')
                sqlite_count = cursor.fetchone()[0]
        except sqlite3.Error as err:
            pytest.fail(
                f'Возникла ошибка, когда происходила проверка данных: {err}'
            )

        try:
            with contextlib.closing(postgres_test_connection.cursor()) \
                    as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM content.{table_name};')
                pg_count = cursor.fetchone()[0]
        except psycopg2.Error as err:
            pytest.fail(
                f'Возникла ошибка, когда происходила проверка данных: {err}'
            )

        assert sqlite_count == pg_count, \
            f'Несоответствие количества строк в таблице {table_name}'


def fetch_data_from_database(
    connection,
    table_name,
    data_class
):
    """
    Fetch data from a database table.

    Args:
        connection: Database connection object (SQLite or PostgreSQL).
        table_name (str): Name of the database table to fetch data from.
        data_class: Class representing the table's data structure.

    Yields:
        tuple: A tuple containing the fetched data.

    Raises:
        sqlite3.Error: If there's an error while accessing the SQLite database.
        psycopg2.Error: If there's an error while accessing the PostgreSQL
            database.
    """
    query = f'SELECT {", ".join(data_class.model_fields)} FROM {table_name}'
    try:
        with contextlib.closing(connection.cursor()) as cursor:
            cursor.execute(query)

            while True:
                rows = cursor.fetchone()
                if not rows:
                    break
                else:
                    yield rows
    except (sqlite3.Error, psycopg2.Error) as err:
        pytest.fail(f'Ошибка доступа к базе данных: {err} in {table_name}')


def from_tuple_to_dict(
    fields: dict,
    data_tuple: tuple
):
    data_dict = {}
    for field, data in zip(fields, data_tuple):
        data_dict[field] = data
    return data_dict


def test_data_consistency(
    sqlite_test_connection: sqlite3.Connection,
    postgres_test_connection: _connection
):
    """
    Method to check the consistency of data counts between SQLite
    and PostgreSQL tables.

    Args:
        sqlite_test_connection (sqlite3.Connection): SQLite connection fixture.
        postgres_test_connection (_connection): PostgreSQL connection fixture.

    Asserts:
        json: Compares rows data between SQLite tables and PostgreSQL tables.
    """
    table_data_mapping = {
        'person': Person,
        'genre': Genre,
        'film_work': Filmwork,
        'person_film_work': PersonFilmwork,
        'genre_film_work': GenreFilmwork,
    }

    for table_name, data_class in table_data_mapping.items():
        sqlite_data_gen = fetch_data_from_database(
            sqlite_test_connection, table_name, data_class
        )

        postgres_data_gen = fetch_data_from_database(
            postgres_test_connection, f'content.{table_name}', data_class
        )

        for sqlite_data, postgres_data in zip(
            sqlite_data_gen,
            postgres_data_gen
        ):
            sqlite_data_dict = from_tuple_to_dict(
                data_class.model_fields.keys(),
                sqlite_data
            )
            postgres_data_dict = from_tuple_to_dict(
                data_class.model_fields.keys(),
                postgres_data
            )

            assert (
                data_class(**sqlite_data_dict).model_dump() ==
                data_class(**postgres_data_dict).model_dump()
            ), f'Несоответствие данных в таблице {table_name}'
