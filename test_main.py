import pytest
from httpx import AsyncClient
from pytest import FixtureRequest
from collections.abc import Iterator
import asyncio
import pytest_asyncio
from asyncio import (
    AbstractEventLoop, 
    get_event_loop_policy
)


from main import app, lifespan

@pytest.fixture(scope="session")
def event_loop(request: FixtureRequest) -> Iterator[AbstractEventLoop]:
    event_loop_policy = get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
def event_loop(request: FixtureRequest) -> Iterator[AbstractEventLoop]:
    event_loop_policy = get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with lifespan(app): 
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

async def create_async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)  # Simulate some delay (adjust as needed)
        yield i

@pytest.mark.asyncio
async def test_root_no_rate_limit(async_client):
    async for _ in create_async_range(5):
        response = await async_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the rate-limited FastAPI app!"}

@pytest.mark.asyncio
async def test_root_rate_limit_exceeded(async_client):
    async for _ in create_async_range(5):
        response = await async_client.get("/")
        assert response.status_code == 200
    response = await async_client.get("/")

    assert response.status_code == 429
    assert response.json() == {"message": "You've reached the rate limit!"}

@pytest.mark.asyncio
async def test_limited_no_rate_limit(async_client):
    async for _ in create_async_range(3):
        response = await async_client.get("/limited")
        assert response.status_code == 200
        assert response.json() == {"message": "This endpoint is limited to 3 requests per minute."}

@pytest.mark.asyncio
async def test_limited_rate_limit_exceeded(async_client):
    async for _ in create_async_range(3):
        response = await async_client.get("/limited")
        assert response.status_code == 200

    response = await async_client.get("/limited")
    assert response.status_code == 429
    assert response.json() == {"message": "You've reached the rate limit!"}

@pytest.mark.asyncio
async def test_open_endpoint(async_client):
    response = await async_client.get("/open")

    assert response.status_code == 200
    assert response.json() == {"message": "This endpoint is not rate-limited."}

# New Test Cases:

@pytest.mark.asyncio
async def test_burst_requests(async_client):
    # Exceed limit async for both endpoints
    async for _ in create_async_range(6):
        response = await async_client.get("/")

    response = await async_client.get("/")
    assert response.status_code == 429  # Limited after exceeding combined rate

@pytest.mark.asyncio
async def test_rate_limit_reset(async_client):
    async for _ in create_async_range(5):
        response = await async_client.get("/")
        assert response.status_code == 200
    await asyncio.sleep(60)  # Wait async for the rate limit window to reset
    response = await async_client.get("/")
    assert response.status_code == 200  # Request allowed after reset

@pytest.mark.asyncio
async def test_custom_exception_handler(async_client):
    async for _ in create_async_range(5):
        response = await async_client.get("/")
        assert response.status_code == 200
    response = await async_client.get("/")
    assert response.status_code == 429
    assert "X-RateLimit-Limit" in response.headers  # Verify custom header

