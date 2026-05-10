from jose import jwt
import pytest
from app import dependencies

@pytest.mark.asyncio
async def test_register_creates_user(auth_client):
    response = await auth_client.post("/auth/register",
        json={"username": "alice", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["username"] == "alice"
    assert "tasks" not in response.json()

@pytest.mark.asyncio
async def test_register_rejects_duplicate_username(auth_client):
    await auth_client.post("/auth/register",
        json={"username": "alice", "password": "password"},
    )

    response = await auth_client.post("/auth/register",
        json={"username": "alice", "password": "another-password"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Такой user уже существует"

@pytest.mark.asyncio
async def test_login_returns_bearer_token(auth_client):
    await auth_client.post("/auth/register",
        json={"username": "alice", "password": "password"},
    )

    response = await auth_client.post(
        "/auth/login",
        data={"username": "alice", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    payload = jwt.decode(
        response.json()["access_token"],
        dependencies.SECRET_KEY,
        algorithms=[dependencies.ALGORITHM],
    )
    assert payload["sub"] == "alice"

@pytest.mark.asyncio
async def test_login_rejects_wrong_password(auth_client):
    await auth_client.post("/auth/register",
        json={"username": "alice", "password": "password"},
    )
    response = await auth_client.post( "/auth/login",
        data={"username": "alice", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "неправильное имя пользователя или пароль"
