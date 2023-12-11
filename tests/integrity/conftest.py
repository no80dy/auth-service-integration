import pytest
import aiohttp
import asyncio
import pytest_asyncio

from redis.asyncio import Redis

from .settings import test_settings


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def fastapi_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
def make_get_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict, headers: dict):
        url = test_settings.SERVICE_URL + f'/movie_service/api/v1/{endpoint}'
        async with fastapi_session.get(url, params=query_data, headers=headers) as response:
            body = await response.json() if response.headers['Content-type'] == 'application/json' else response.text()
            headers = response.headers
            status = response.status

            response = {
                'body': body,
                'headers': headers,
                'status': status
            }
            return response
    return inner


@pytest_asyncio.fixture(scope='function')
async def redis_client() -> Redis:
    async with Redis(host=test_settings.REDIS_HOST, port=test_settings.REDIS_PORT) as client:
        yield client


@pytest.fixture(scope='function', autouse=True)
async def clear_redis(redis_client):
    """Fixture to clear Redis data."""
    # Your clearing logic here, for example:
    await redis_client.flushdb()
