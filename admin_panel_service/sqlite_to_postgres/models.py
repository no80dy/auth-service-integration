import uuid
import datetime

from dataclasses import dataclass, field


@dataclass
class Person:
    """Структура данных для таблицы person"""
    full_name: str

    created_at: datetime.datetime
    updated_at: datetime.datetime

    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Filmwork:
    """Структура данных для таблицы film_work"""
    title: str
    description: str
    creation_date: datetime.date
    file_path: str
    type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    rating: float = field(default=0.0)


@dataclass
class Genre:
    """Структура данных для таблицы genre"""
    name: str
    description: str

    created_at: datetime.datetime
    updated_at: datetime.datetime

    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PersonFilmwork:
    """Структура данных для таблицы person_film_work"""
    role: str
    created_at: datetime.datetime
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class GenreFilmwork:
    """Структура данных для таблицы genre_film_work"""
    created_at: datetime.datetime
    genre_id: uuid.uuid4 = field(default_factory=uuid.uuid4)
    film_work_id: uuid.uuid4 = field(default_factory=uuid.uuid4)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
