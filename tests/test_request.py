from io import BytesIO

import pytest

from restcraft import RestCraft
from restcraft.http import Request


def test_request_method():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "POST",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.method == "POST"
    Request.clear()


def test_request_path():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/example/path",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.path == "/example/path"
    Request.clear()


def test_request_headers():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "wsgi.input": BytesIO(),
        "HTTP_CUSTOM_HEADER": "HeaderValue",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": "123",
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    print(request.headers)

    assert request.headers["custom-header"] == "HeaderValue"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["content-length"] == "123"
    Request.clear()


def test_request_is_secure():
    app = RestCraft(config=object())
    secure_environ = {
        "REQUEST_METHOD": "GET",
        "wsgi.input": BytesIO(),
        "wsgi.url_scheme": "https",
        "PATH_INFO": "/",
        "wsgi.application": app,
    }
    insecure_environ = {
        "REQUEST_METHOD": "GET",
        "wsgi.input": BytesIO(),
        "wsgi.url_scheme": "http",
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(secure_environ)
    request = Request.current()
    assert request.is_secure is True

    Request.clear()

    Request.bind(insecure_environ)
    request = Request.current()
    assert request.is_secure is False

    Request.clear()


def test_request_content_type():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "CONTENT_TYPE": "application/json",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.content_type == "application/json"
    Request.clear()


def test_request_content_length():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "CONTENT_LENGTH": "256",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.content_length == 256
    Request.clear()


def test_request_query():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "QUERY_STRING": "key1=value1&key2=value2&key2=value3",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.query == {"key1": "value1", "key2": ["value2", "value3"]}
    Request.clear()


def test_request_forms():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "CONTENT_LENGTH": "11",
        "wsgi.input": BytesIO(b"key=value"),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.forms == {"key": "value"}
    Request.clear()


def test_request_files():
    app = RestCraft(config=object())
    boundary = "WebKitFormBoundary"
    data = b"""--WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="test.txt"
Content-Type: text/plain

file content
--WebKitFormBoundary
Content-Disposition: form-data; name="file2"

lsfratel
--WebKitFormBoundary--"""
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": f"multipart/form-data; boundary={boundary}",
        "CONTENT_LENGTH": str(len(data)),
        "wsgi.input": BytesIO(data),
        "PATH_INFO": "/upload",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()
    file_data = request.files["file"]
    field_data = request.forms["file2"]

    assert file_data["filename"] == "test.txt"
    assert file_data["content_type"] == "text/plain"

    assert field_data == "lsfratel"
    Request.clear()


def test_request_json():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": "17",
        "wsgi.input": BytesIO(b'{"key": "value"}'),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.json == {"key": "value"}
    Request.clear()


def test_request_bind_and_clear():
    app = RestCraft(config=object())
    environ = {
        "REQUEST_METHOD": "GET",
        "wsgi.input": BytesIO(),
        "PATH_INFO": "/",
        "wsgi.application": app,
    }

    Request.bind(environ)
    request = Request.current()

    assert request.path == "/"

    Request.clear()

    with pytest.raises(RuntimeError):
        Request.current()
