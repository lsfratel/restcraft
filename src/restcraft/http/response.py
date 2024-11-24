import json
from http.client import responses as http_responses
from typing import Any


def make_headers(headers: dict[str, str]) -> dict[str, str]:
    if headers is None:
        return {}

    return {k.lower(): v for k, v in headers.items()}


class Response:
    default_content_type = "text/plain; charset=utf-8"

    __slots__ = ("_body", "_status", "_headers")

    def __init__(
        self, body: Any = None, status: int = 200, headers: None | dict[str, str] = None
    ):
        self._body = body
        self._status = status
        self._headers = make_headers(headers or {})

    @property
    def status(self):
        return f"{self._status} {http_responses.get(self._status, 'Unknown')}"

    @status.setter
    def status(self, value: int):
        self._status = value

    @property
    def status_text(self):
        return f"{self._status} {http_responses.get(self._status, 'Unknown')}"

    @property
    def headers(self):
        if "content-type" not in self._headers:
            self._headers["content-type"] = self.default_content_type

        return self._headers

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: str):
        self._body = value

    @property
    def body_encoded(self) -> bytes:
        if self._body is None:
            return b""

        return self._body.encode("utf-8")

    def to_wsgi(self):
        body = self.body_encoded

        if "content-length" not in self.headers:
            self.headers["content-length"] = str(len(body))

        headers = list(self.headers.items())

        return self.status_text, headers, body


class JSONResponse(Response):
    default_content_type = "application/json; charset=utf-8"

    @property
    def body_encoded(self) -> bytes:
        if self.body is None:
            return b""

        return json.dumps(self.body).encode("utf-8")
