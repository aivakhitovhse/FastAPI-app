from datetime import timedelta
from jose import jwt
from app import dependencies

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
        expires_delta=timedelta(minutes=5),
    )
    payload = jwt.decode(token, dependencies.SECRET_KEY, algorithms=[dependencies.ALGORITHM],
    )
    assert payload["sub"] == "test-user"
    assert "exp" in payload
