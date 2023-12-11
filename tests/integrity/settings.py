from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    PROJECT_NAME: str = 'movies'

    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379

    ES_HOST: str = 'elastic'
    ES_PORT: int = 9200

    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = '123qwe'
    POSTGRES_HOST: str = 'db'
    POSTGRES_PORT: int = 5432

    SERVICE_URL: str = 'http://nginx'

    BACKOFF_MAX_TIME: int = 60


test_settings = TestSettings()
