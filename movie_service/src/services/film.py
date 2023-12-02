import json
import uuid
from functools import lru_cache
from typing import Any
from abc import ABC, abstractmethod

from fastapi import Depends

from db.cache import get_cache
from db.redis import ICache
from db.storage import get_elastic
from db.elastic import ElasticStorage, IStorage
from models.film import Film
from models.person import Person
from core.config import settings


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def calculate_offset(page_size: int, page_number: int) -> int:
    return (page_number - 1) * page_size


def get_sort_field(sort: str) -> str:
    return sort[1:] if sort.startswith('-') else sort


def get_sort_order(sort: str) -> str:
    return 'desc' if sort.startswith('-') else 'asc'


class StorageFilmHandler(ABC):
    def __init__(
        self,
        storage: IStorage
    ) -> None:
        self.storage = storage

    @abstractmethod
    async def get_film_by_id(
        self,
        film_id: uuid.UUID
    ) -> Film | None:
        pass

    @abstractmethod
    async def get_films_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        pass

    @abstractmethod
    async def get_films_with_sort(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        pass

    @abstractmethod
    async def get_films_by_genre_id_with_sort(
        self,
        genre_id: uuid.UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        pass

    @abstractmethod
    async def get_films_by_ids(
        self,
        film_ids: list[str]
    ) -> list[Film] | None:
        pass


class CacheFilmHandler:
    """Класс CacheFilmHandler отвечает за работу с кешом по информации о фильмах."""

    def __init__(self, cache: ICache, expired_time: int) -> None:
        self.cache = cache
        self.expired_time = expired_time

    async def get_film(self, key: str) -> None | Film | list[Film] | Any:
        data = await self.cache.get(key)
        if not data:
            return None

        if '/' not in key:
            return Film.model_validate_json(data)
        return [Film.model_validate_json(obj) for obj in json.loads(data)]

    async def put_film(self, key: str, value: Any):
        await self.cache.set(key, value, self.expired_time)


class ElasticFilmHandler(StorageFilmHandler):
    """Класс ElasticFilmHandler отвечает за работу с эластиком по информации о фильмах."""

    def __init__(self, storage: ElasticStorage) -> None:
        super().__init__(storage)

    async def get_film_by_id(
        self,
        film_id: uuid.UUID
    ) -> Film | None:
        doc = await self.storage.get_by_id(
            index=settings.es_movies_index, id=str(film_id)
        )
        if not doc:
            return None
        return Film(**doc)

    async def get_films_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        elastic_query = {
            'query': {
                'fuzzy': {
                    'title': {
                        'value': query,
                        'fuzziness': 'AUTO'
                    }
                }
            },
            'size': page_size,
            'from': calculate_offset(page_size, page_number)
        }

        docs = await self.storage.search(
            index=settings.es_movies_index, body=elastic_query
        )
        if not docs:
            return None
        return [Film(**doc) for doc in docs]

    async def get_films_with_sort(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        elastic_query = {
            'sort': [
                {
                    get_sort_field(sort): {
                        'order': get_sort_order(sort)
                    }
                }
            ],
            'size': page_size,
            'from': calculate_offset(page_size, page_number)
        }

        docs = await self.storage.search(
            index=settings.es_movies_index, body=elastic_query
        )
        if not docs:
            return None
        return [Film(**doc) for doc in docs]

    async def get_films_by_genre_id_with_sort(
        self,
        genre_id: uuid.UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film] | None:
        elastic_query = {
            'query': {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'match': {
                            'genres.id': genre_id
                        }
                    }
                }
            },
            'sort': [
                {
                    get_sort_field(sort): {
                        'order': get_sort_order(sort)
                    }
                }
            ],
            'size': page_size,
            'from': calculate_offset(page_size, page_number)
        }

        docs = await self.storage.search(
            index=settings.es_movies_index, body=elastic_query
        )
        if not docs:
            return None
        return [Film(**doc) for doc in docs]

    async def get_films_by_ids(
        self,
        film_ids: list[str],
    ) -> list[Film] | None:
        elastic_query = {
            'query': {
                'ids': {
                    'values': film_ids
                }
            }
        }

        docs = await self.storage.search(
            index=settings.es_movies_index, body=elastic_query
        )
        if not docs:
            return None
        return [Film(**doc) for doc in docs]


class FilmService:
    """Класс FilmService содержит бизнес-логику по работе с фильмами."""

    def __init__(
        self,
        cache_handler: CacheFilmHandler,
        storage_handler: ElasticFilmHandler
    ) -> None:
        self.cache_handler = cache_handler
        self.storage_handler = storage_handler

    async def get_film_by_id(self, film_id: uuid.UUID) -> Film | None:
        film = await self.cache_handler.get_film(str(film_id))
        if not film:
            film = await self.storage_handler.get_film_by_id(film_id)
            if not film:
                return None

            await self.cache_handler.put_film(film.model_dump_json(), str(film_id))

        return film

    async def get_films_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{query}/{page_size}/{page_number}'
        films = await self.cache_handler.get_film(key)
        if not films:
            films = await self.storage_handler.get_films_by_query(
                query, page_size, page_number
            )

            if not films:
                return []
            value = json.dumps([film.model_dump_json() for film in films])
            await self.cache_handler.put_film(key, value)

        return films

    async def get_films_with_sort(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{sort}/{page_size}/{page_number}'
        films = await self.cache_handler.get_film(key)
        if not films:
            films = await self.storage_handler.get_films_with_sort(
                sort, page_size, page_number
            )
            if not films:
                return []
            value = json.dumps([film.model_dump_json() for film in films])
            await self.cache_handler.put_film(value, key)

        return films

    async def get_films_by_genre_id_with_sort(
        self,
        genre_id: uuid.UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{genre_id}/{sort}/{page_size}/{page_number}'
        films = await self.cache_handler.get_film(key)
        if not films:
            films = await self.storage_handler.get_films_by_genre_id_with_sort(
                genre_id, sort, page_size, page_number
            )
            if not films:
                return []
            value = json.dumps([film.model_dump_json() for film in films])
            await self.cache_handler.put_film(value, key)

        return films

    async def get_person_films(
        self,
        person: Person,
    ) -> list[Film]:

        film_ids = [str(film.id) for film in person.films]

        key = '/'.join(film_ids)
        films = await self.cache_handler.get_film(key)
        if not films:
            films = await self.storage_handler.get_films_by_ids(film_ids)
            if not films:
                return []
            if len(films) == 1:
                value = films[0].model_dump_json()
            else:
                value = json.dumps([film.model_dump_json() for film in films])
            await self.cache_handler.put_film(key, value)

        return films if type(films) == list else [films]


@lru_cache()
def get_film_service(
    cache: ICache = Depends(get_cache),
    elastic: ElasticStorage = Depends(get_elastic),
) -> FilmService:
    cache_handler = CacheFilmHandler(cache, FILM_CACHE_EXPIRE_IN_SECONDS)
    storage_handler = ElasticFilmHandler(elastic)

    return FilmService(cache_handler, storage_handler)
