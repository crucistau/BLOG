import pytest

from app.dependencies.auth import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    hashed = hash_password("hello123")
    assert verify_password("hello123", hashed)
    assert not verify_password("wrong", hashed)


def test_token_roundtrip():
    token = create_access_token(42)
    user_id = decode_token(token)
    assert user_id == 42


def test_invalid_token():
    with pytest.raises(Exception):
        decode_token("bad-token")
