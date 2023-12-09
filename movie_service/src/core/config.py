import os

from core.logger import LOGGING
from pydantic_settings import BaseSettings
from logging import config as logging_config


class Settings(BaseSettings):
    project_name: str = 'movies'
    redis_host: str = 'redis'
    redis_port: int = 6379
    es_host: str = 'elastic'
    es_port: int = 9200

    es_movies_index: str = 'movies'
    es_genres_index: str = 'genres'
    es_persons_index: str = 'persons'

    jwt_secret_key: str = 'secret'
    jwt_algorithm: str = 'HS256'


settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
