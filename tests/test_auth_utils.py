from datetime import timedelta
import pytest
from jose import jwt
from app import crud, dependencies, schemas

def test_password_hash_is_not_plain_password():
    password = "super-secret-password"
    hashed_password = dependencies.get_password_hash(password)
    assert hashed_password != password

def test_verify_password_accepts_correct_password():
    password = "super-secret-password"
    hashed_password = dependencies.get_password_hash(password)
    assert dependencies.verify_password(password, hashed_password) is True

def test_verify_password_rejects_wrong_password():
    hashed_password = dependencies.get_password_hash("correct-password")
    assert dependencies.verify_password("wrong-password", hashed_password) is False

def test_create_access_token_contains_subject():
    token = dependencies.create_access_token(data={"sub": "test-user"},
        expires_delta=timedelta(minutes=5),)
    payload = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM],)
    assert payload["sub"] == "test-user"
    assert "exp" in payload

def test_create_access_token_uses_default_expiration():
    token = dependencies.create_access_token(data={"sub": "test-user"})
    payload = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM])

    assert payload["sub"] == "test-user"
    assert "exp" in payload

@pytest.mark.asyncio
async def test_get_current_user_returns_user_for_valid_token(test_session_maker):
    async with test_session_maker() as session:
        user = await crud.create_user(session,schemas.UserCreate(username="alice", password="password"),
            hashed_password="hashed-password",
        )
        token = dependencies.create_access_token(data={"sub": "alice"})
        current_user = await dependencies.get_current_user(token=token, db=session)

    assert current_user.id == user.id
    assert current_user.username == "alice"

@pytest.mark.asyncio
async def test_get_current_user_rejects_token_without_subject(test_session_maker):
    token = dependencies.create_access_token(data={"user": "alice"})
    async with test_session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await dependencies.get_current_user(token=token, db=session)

    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(test_session_maker):
    async with test_session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await dependencies.get_current_user(token="not-a-valid-token", db=session)

    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user(test_session_maker):
    token = dependencies.create_access_token(data={"sub": "missing-user"})
    async with test_session_maker() as session:
        with pytest.raises(Exception) as exc_info:
            await dependencies.get_current_user(token=token, db=session)

    assert exc_info.value.status_code == 401
