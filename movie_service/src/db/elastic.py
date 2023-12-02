from typing import Any
from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError


class IStorage(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, id: str) -> dict | None:
        pass

    @abstractmethod
    async def search(self, index: str, body: Any) -> list[dict] | None:
        pass

    @abstractmethod
    async def close(self):
        pass


class ElasticStorage(IStorage):
    def __init__(self, **kwargs) -> None:
        self.connection = AsyncElasticsearch(**kwargs)

    async def get_by_id(self, index: str, id: str) -> dict | None:
        try:
            doc = await self.connection.get(index=index, id=id)
        except NotFoundError:
            return None
        return doc['_source']

    async def search(self, index: str, body: Any) -> list[dict] | None:
        try:
            docs = await self.connection.search(
                index=index, body=body
            )
        except NotFoundError:
            return None
        return [doc['_source'] for doc in docs['hits']['hits']]

    async def close(self):
        await self.connection.close()
