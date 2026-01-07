from datetime import timedelta
from user_service.app.auth import auth


def test_hash_and_verify_password():
    pwd = "secretpassword"
    hashed = auth.hash_password(pwd)

    assert hashed != pwd
    assert auth.verify_password(pwd, hashed) is True
    assert auth.verify_password("wrong", hashed) is False


def test_jwt_creation_and_decoding():
    data = {"sub": "testuser", "uuid": "123"}
    token = auth.create_access_token(data, expires_delta=timedelta(minutes=10))

    assert isinstance(token, str)

    decoded = auth.decode_access_token(token)
    assert decoded["sub"] == "testuser"
    assert decoded["uuid"] == "123"


def test_decode_invalid_token():
    res = auth.decode_access_token("invalid.token.here")
    assert res == {}