import asyncio
import httpx


async def test_rate_limit():
    async with httpx.AsyncClient() as client:
        for _ in range(20):
            response = await client.get("http://localhost/movie_service/api/openapi")
            print(f"Status Code: {response.status_code}, Content: {response.text}")

asyncio.run(test_rate_limit())
