# настройки для тестов
import logging

from pydantic_settings import BaseSettings

from .testdata.es_mapping import es_shema_movies, es_shema_persons, es_shema_genres


class TestSettings(BaseSettings):
    project_name: str = 'movies'

    redis_host: str = 'redis'
    redis_port: int = 6379

    es_host: str = 'elastic'
    es_port: int = 9200
    es_id_field: str = 'id'
    es_index_movies_mapping: dict = es_shema_movies
    es_index_persons_mapping: dict = es_shema_persons
    es_index_genres_mapping: dict = es_shema_genres

    es_movies_index: str = 'movies'
    es_persons_index: str = 'persons'
    es_genres_index: str = 'genres'

    service_url: str = 'http://fastapi:8000'


test_settings = TestSettings()
