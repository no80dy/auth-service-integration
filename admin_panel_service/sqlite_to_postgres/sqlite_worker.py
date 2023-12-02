import sqlite3
import logging
import contextlib

from models import (
    Person,
    Genre,
    Filmwork,
    PersonFilmwork,
    GenreFilmwork
)


class SQLiteExtractor:
    """Класс для загрузки данных в SQLite"""
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row

    def extract_data_from_table(self, table_name, data_class, page_size=100):
        """Метод извлечения данных из таблицы"""
        try:
            with contextlib.closing(self.connection.cursor()) as cursor:
                cursor.execute(f'SELECT * FROM {table_name};')
                while True:
                    rows = cursor.fetchmany(page_size)
                    if not rows:
                        break
                    yield [data_class(**row) for row in rows]
        except sqlite3.Error as sqlite_error:
            logging.error(f'SQLite: {sqlite_error}')

    def extract_all_data(self):
        """Метод извлечения данных из таблиц SQLite"""
        data = {}
        for table_name, data_class in [
            ('person', Person),
            ('genre', Genre),
            ('film_work', Filmwork),
            ('person_film_work', PersonFilmwork),
            ('genre_film_work', GenreFilmwork),
        ]:
            data[table_name] = self.extract_data_from_table(
                table_name, data_class
            )
        return data
