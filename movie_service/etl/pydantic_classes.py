import os
import uuid
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PG_DB_NAME: str
    PG_DB_USER: str
    PG_DB_PASSWORD: str
    PG_DB_HOST: Optional[str] = '127.0.0.1'
    PG_DB_PORT: int

    ES_HOST: Optional[str] = '127.0.0.1'
    ES_PORT: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), 'etl.env'), env_file_encoding='utf-8')


class Genre(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None


class PersonFilm(BaseModel):
    id: uuid.UUID = Field(alias='film_work_id')
    roles: list[str]


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    films: list[PersonFilm]
