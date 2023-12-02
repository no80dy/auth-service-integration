from db.elastic import ElasticStorage


es: ElasticStorage | None = None


async def get_elastic() -> ElasticStorage:
    return es
