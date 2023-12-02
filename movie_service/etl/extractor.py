from psycopg2.extensions import connection as _connection

from helper import logger
from sql_queries import sql_genres, sql_persons


class PostgresExtractor:
    """Класс для работы с базой данной Postgres"""

    def __init__(self, connection: _connection, schema: str) -> None:
        self.conn = connection
        if schema in ('genres', 'persons'):
            self.schema = schema
        else:
            raise ValueError(
                f'{self.__class__.__name__}: Unknown schema name: {schema}')

    def extract_data(self, state: str, batch_size=50) -> list[tuple]:
        """Метод для получения информации по всем измененным жанрам, которые есть в фильмах."""
        if self.schema == 'genres':
            sql_query = sql_genres.format(state)
        elif self.schema == 'persons':
            sql_query = sql_persons.format(state)

        try:
            with self.conn.cursor()as self.curs:
                self.curs.execute(sql_query)
                while True:
                    records = self.curs.fetchmany(size=batch_size)
                    if not records:
                        break
                    yield records
        except Exception as e:
            logger.error(f'{self.__class__.__name__}: {e}')
