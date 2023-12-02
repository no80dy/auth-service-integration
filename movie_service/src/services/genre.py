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
from models.genre import Genres
from core.config import settings


GENRE_CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min


class StorageGenreHandler(ABC):
    def __init__(self, storage: IStorage):
        self.storage = storage

    @abstractmethod
    async def get_genre_by_id(self, genre_id: uuid.UUID) -> Genres | None:
        pass

    @abstractmethod
    async def get_genres(self) -> list[Genres] | None:
        pass


class CacheGenreHandler:
    """Класс CacheGenreHandler отвечает за работу с кешом по информации о жанрах."""

    def __init__(self, cache: ICache, expired_time: int) -> None:
        self.cache = cache
        self.expired_time = expired_time

    async def get_genre(self, key: str) -> None | Genres | list[Genres] | Any:
        data = await self.cache.get(key)
        if not data:
            return None

        if key != 'genres':
            return Genres.model_validate_json(data)
        return [Genres.model_validate_json(obj) for obj in json.loads(data)]

    async def put_genre(self, value: Any, key: str):
        await self.cache.set(value, key, self.expired_time)


class ElasticGenreHandler(StorageGenreHandler):
    """Класс ElasticGenreHandler отвечает за работу с эластиком по информации о жанрах."""

    def __init__(self, storage: ElasticStorage) -> None:
        super().__init__(storage)

    async def get_genre_by_id(
        self,
        genre_id: uuid.UUID
    ) -> Genres | None:
        doc = await self.storage.get_by_id(
            index=settings.es_genres_index, id=str(genre_id)
        )
        if not doc:
            return None
        return Genres(**doc)

    async def get_genres(self) -> list[Genres] | None:
        query = {
            'query': {
                'match_all': {}
            },
            'size': 1000
        }

        docs = await self.storage.search(
            index=settings.es_genres_index, body=query
        )
        if not docs:
            return None
        return [Genres(**doc) for doc in docs]


class GenreService:
    """Класс GenreService содержит бизнес-логику по работе с жанрами."""

    def __init__(
        self,
        cache_handler: CacheGenreHandler,
        storage_handler: ElasticGenreHandler
    ) -> None:
        self.cache_handler = cache_handler
        self.storage_handler = storage_handler

    async def get_genre_by_id(
        self,
        genre_id: uuid.UUID
    ) -> Genres | None:
        genre = await self.cache_handler.get_genre(str(genre_id))
        if not genre:
            genre = await self.storage_handler.get_genre_by_id(genre_id)
            if not genre:
                return None

            await self.cache_handler.put_genre(genre.model_dump_json(), str(genre_id))
        return genre

    async def get_genres(self) -> list[Genres]:
        genres = await self.cache_handler.get_genre('genres')
        if not genres:
            genres = await self.storage_handler.get_genres()
            if not genres:
                return []
            value = json.dumps([genre.model_dump_json() for genre in genres])
            await self.cache_handler.put_genre(value, 'genres')

        return genres


@lru_cache()
def get_genre_service(
    cache: ICache = Depends(get_cache),
    elastic: ElasticStorage = Depends(get_elastic),
) -> GenreService:
    cache_handler = CacheGenreHandler(cache, GENRE_CACHE_EXPIRE_IN_SECONDS)
    storage_handler = ElasticGenreHandler(elastic)
    return GenreService(cache_handler, storage_handler)
