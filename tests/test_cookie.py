import base64
from datetime import datetime, timedelta

import pytest

from restcraft.http.cookie import Cookie, make_expires


def test_make_expires_with_datetime():
    future_time = datetime(2023, 1, 1, 12, 0, 0)
    result = make_expires(future_time)
    assert result == "Sun, 01-Jan-2023 12:00:00 GMT"


def test_make_expires_with_int():
    seconds_from_now = 3600  # 1 hour
    result = make_expires(seconds_from_now)
    future_time = (datetime.now() + timedelta(seconds=seconds_from_now)).strftime(
        "%a, %d-%b-%Y %H:%M:%S GMT"
    )
    assert result == future_time


def test_make_expires_invalid_input():
    with pytest.raises(ValueError):
        make_expires("invalid_date")


def test_cookie_serialize_unsigned():
    cookie = Cookie("test_cookie", options={"http_only": True, "secure": True})
    serialized = cookie.serialize({"key": "value"})
    assert "test_cookie=" in serialized
    assert '\\"key\\": \\"value\\"' in serialized


def test_cookie_parse_unsigned():
    cookie = Cookie("test_cookie")
    serialized = cookie.serialize({"key": "value"})
    parsed = cookie.parse(serialized)
    assert parsed == {"key": "value"}


def test_cookie_serialize_signed():
    cookie = Cookie(
        "secure_cookie", options={"secrets": ["secret1", "secret2"], "http_only": True}
    )
    serialized = cookie.serialize({"user_id": 42})
    assert "secure_cookie=" in serialized

    cookie_value = serialized.replace('"', "").split("=", 1)[1].split(";")[0]
    data, signature = cookie_value.split(".")
    assert cookie._verify(base64.urlsafe_b64decode(data).decode(), signature) is True


def test_cookie_parse_signed():
    cookie = Cookie("secure_cookie", options={"secrets": ["secret1", "secret2"]})
    serialized = cookie.serialize({"user_id": 42})
    parsed = cookie.parse(serialized)
    assert parsed == {"user_id": 42}


def test_cookie_parse_signed_invalid_signature():
    cookie = Cookie("secure_cookie", options={"secrets": ["secret1", "secret2"]})
    serialized = cookie.serialize({"user_id": 42})

    tampered = serialized.replace(".", "b")
    parsed = cookie.parse(tampered)
    assert parsed is None


def test_cookie_serialize_with_expiry():
    cookie = Cookie("expiring_cookie")
    serialized = cookie.serialize({"key": "value"}, overrides={"expires": 3600})
    assert "expires=" in serialized


def test_cookie_parse_missing_name():
    cookie = Cookie("missing_cookie")
    parsed = cookie.parse("some_other_cookie=value")
    assert parsed is None
