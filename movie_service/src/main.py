from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn

from fastapi import FastAPI
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.v1 import films, genres, persons
from core.config import settings

from db.redis import RedisCache
from db.elastic import ElasticStorage

from db import cache
from db import storage


REQUEST_LIMIT_PER_MINUTE = 20


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.cache = RedisCache(
        host=settings.redis_host, port=settings.redis_port
    )
    storage.es = ElasticStorage(
        hosts=[f'{settings.es_host}:{settings.es_port}', ]
    )
    yield
    await cache.cache.close()
    await storage.es.close()


app = FastAPI(
    description='Информация о фильмах, жанрах и людях, участвовавших в создании произведения',
    version='1.0.0',
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=settings.project_name,
    # Адрес документации в красивом интерфейсе
    docs_url='/movie_service/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/movie_service/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)


@app.middleware('http')
async def rate_limit(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    pipe = await cache.cache.pipeline()
    now = datetime.now()

    key = f'{request_id}:{now.minute}'
    pipe.incr(key, 1)
    pipe.expire(key, 59)
    result = await pipe.execute()
    request_number = result[0]

    if request_number > REQUEST_LIMIT_PER_MINUTE:
        return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content='Rate limit exceeded')
    return response


app.include_router(films.router, prefix='/movie_service/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/movie_service/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/movie_service/api/v1/genres', tags=['genres'])


if __name__ == '__main__':
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
