import json
from http.client import responses as http_responses
from typing import Any


def make_headers(headers: dict[str, str]) -> dict[str, str]:
    if headers is None:
        return {}

    return {k.lower(): v for k, v in headers.items()}


class Response:
    """Base class for HTTP responses."""

    default_content_type = "text/plain; charset=utf-8"

    def __init__(
        self, body: Any = None, status: int = 200, headers: None | dict[str, str] = None
    ):
        self._body = body
        self._status = status
        self._headers = make_headers(headers or {})

    @property
    def status(self):
        """Get the HTTP status code.

        Returns:
            int: the HTTP status code
        """
        return self._status

    @status.setter
    def status(self, value: int):
        self._status = value

    @property
    def status_text(self):
        """Get the HTTP status text.

        Returns:
            str: The HTTP status code and its corresponding text description.
        """
        return f"{self._status} {http_responses.get(self._status, 'Unknown')}"

    @property
    def headers(self):
        """Get the response headers, ensuring Content-Type is set.

        If the "content-type" header is not present in the response headers,
        it sets the default content type.

        Returns:
            dict[str, str]: The response headers.
        """
        if "content-type" not in self._headers:
            self._headers["content-type"] = self.default_content_type

        return self._headers

    @property
    def body(self):
        """Get the HTTP response body.

        Returns:
            Any: The content of the HTTP response body.
        """
        return self._body

    @body.setter
    def body(self, value: str):
        self._body = value

    @property
    def body_encoded(self) -> bytes:
        """Encodes the HTTP response body as bytes.

        If the body is None, this method returns an empty bytes object.
        Otherwise, it encodes the body as UTF-8 bytes and returns the
        result.

        Returns:
            bytes: the encoded HTTP response body
        """

        if self._body is None:
            return b""

        return self._body.encode("utf-8")

    def to_wsgi(self):
        """Convert the response to a WSGI tuple.

        Returns:
            tuple[str, list[tuple[str, str]], bytes]
        """

        body = self.body_encoded

        if "content-length" not in self.headers:
            self.headers["content-length"] = str(len(body))

        headers = list(self.headers.items())

        return self.status_text, headers, body


class JSONResponse(Response):
    """A JSON HTTP response class."""

    default_content_type = "application/json; charset=utf-8"

    @property
    def body_encoded(self) -> bytes:
        """Encodes the HTTP response body as JSON bytes.

        Returns:
            bytes: The JSON-encoded response body.
        """
        if self.body is None:
            return b""

        return json.dumps(self.body).encode("utf-8")
