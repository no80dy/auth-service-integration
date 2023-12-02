# файл со всеми общими фикстурами для тестов.

import aiohttp
import pytest_asyncio

from .settings import test_settings


@pytest_asyncio.fixture(scope='function')
def make_get_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict):
        url = test_settings.service_url + f'/api/v1/{endpoint}'
        async with fastapi_session.get(url, params=query_data) as response:
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
