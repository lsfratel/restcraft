from restcraft.http.response import JSONResponse, Response


def test_response():
    response = Response(body="Hello, World!", status=200)
    status, headers, body = response.to_wsgi()

    assert status == "200 OK"
    assert body == b"Hello, World!"
    assert headers == [
        ("content-type", "text/plain; charset=utf-8"),
        ("content-length", "13"),
    ]


def test_json_response():
    response = JSONResponse(body={"key": "value"}, status=201)
    status, headers, body = response.to_wsgi()

    assert status == "201 Created"
    assert body == b'{"key": "value"}'
    assert headers == [
        ("content-type", "application/json; charset=utf-8"),
        ("content-length", "16"),
    ]
