import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app, root


@pytest.mark.asyncio
async def test_root_function_returns_greeting():
    response = await root()

    assert response == {"message": "Hello there!"}


@pytest.mark.asyncio
async def test_app_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello there!"}
