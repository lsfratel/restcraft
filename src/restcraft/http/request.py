from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qs

from restcraft.contrib.http import MultipartParser
from restcraft.exceptions import RestCraftException
from restcraft.utils import make_fields

if TYPE_CHECKING:
    from typing import Any

    from restcraft.restcraft import RestCraft


class Request:
    """Request object."""

    _local = threading.local()

    def __init__(self, environ: dict[str, Any]):
        self.ENV = environ
        self._query: dict[str, Any] = {}
        self._forms: dict[str, Any] = {}
        self._files: dict[str, Any] = {}
        self._json: dict[str, Any] = {}
        self._headers: dict[str, str] = {}
        self.__parsed_body = False
        self.__parsed_query = False

    def _max_body_size(self):
        """Get the maximum body size for the current request.

        Returns:
            int: the maximum body size in bytes
        """

        return int(getattr(self.app.config, "MAX_BODY_SIZE", 10 * 1024 * 1024))

    def _parse_body(self):
        """Parse the request body.

        Raises:
            RestCraftException: if the request body is too large or invalid
        """

        if self.__parsed_body:
            return

        self.__parsed_body = True

        if self.method not in ("POST", "PUT", "PATCH"):
            return

        clength = self.content_length

        if clength < 1:
            return

        try:
            if clength > self._max_body_size():
                raise RestCraftException(
                    "Failed to parse request body",
                    errors={"body": "Request body is too large"},
                    status=413,
                )

            ctype = self.content_type.split(";")[0]

            if not ctype:
                raise RestCraftException(
                    "Failed to parse request body",
                    errors={"headers": "Missing Content-Type header"},
                    status=400,
                )

            if ctype == "application/json":
                stream = self.ENV["wsgi.input"]
                data = stream.read(clength)
                if not data:
                    return self._json
                self._json = json.loads(data.decode(self.charset))
            elif ctype == "application/x-www-form-urlencoded":
                stream = self.ENV["wsgi.input"]
                self._forms = make_fields(
                    parse_qs(stream.read(clength).decode(self.charset))
                )
            elif ctype == "multipart/form-data":
                parser = MultipartParser(self.ENV, max_body_size=self._max_body_size())
                forms, files = parser.parse()

                self._forms = make_fields(forms)
                self._files = make_fields(files)
        except RestCraftException:
            raise
        except Exception as e:
            message = "Failed to parse request body"
            errors = {"description": str(e)}
            raise RestCraftException(message, errors=errors, status=400) from e

    @property
    def app(self) -> RestCraft:
        """Get the RestCraft application.

        Returns:
            RestCraft: the RestCraft application
        """

        return self.ENV["wsgi.application"]

    @property
    def origin(self):
        """Get the origin for the current request.

        Returns:
            str: the origin
        """

        return self.ENV.get("HTTP_ORIGIN", "")

    @property
    def method(self):
        """Get the HTTP method for the current request.

        Returns:
            str: the HTTP method
        """

        return self.ENV.get("REQUEST_METHOD", "GET").upper()

    @property
    def headers(self):
        """Get the request headers.

        Returns:
            dict[str, str]: the request headers
        """

        if self._headers:
            return self._headers

        for k, v in self.ENV.items():
            if k.startswith("HTTP_"):
                self._headers[k[5:].replace("_", "-").lower()] = cast(str, v)

            if k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                self._headers[k.replace("_", "-").lower()] = cast(str, v)

        return self._headers

    @property
    def charset(self):
        """Get the character encoding for the current request.

        Returns:
            str: the character encoding
        """

        if "charset=" in self.content_type:
            return self.content_type.split("charset=")[1].split(";")[0]

        return "utf-8"

    @property
    def is_secure(self):
        """Check if the current request is secure.

        Returns:
            bool: True if the request is secure, False otherwise
        """

        return self.ENV.get("wsgi.url_scheme", "http") == "https"

    @property
    def path(self) -> str:
        """Get the URL path for the current request.

        Returns:
            str: the URL path
        """

        return self.ENV.get("PATH_INFO", "/")

    @property
    def content_type(self) -> str:
        """Get the Content-Type header for the current request.

        Returns:
            str: the Content-Type header
        """

        return self.ENV.get("CONTENT_TYPE", "")

    @property
    def content_length(self) -> int:
        """Get the Content-Length header for the current request.

        Returns:
            int: the Content-Length header
        """

        return int(self.ENV.get("CONTENT_LENGTH", 0))

    @property
    def query(self):
        """Get the query string for the current request.

        Returns:
            dict[str, Any]: the query string
        """

        if self.__parsed_query:
            return self._query

        self.__parsed_query = True

        qs: str = self.ENV.get("QUERY_STRING", "")

        if not qs:
            return self._query

        self._query = make_fields(parse_qs(qs, keep_blank_values=True))

        return self._query

    @property
    def forms(self):
        """Get the form data for the current request.

        Returns:
            dict[str, Any]: the form data
        """

        if not self.__parsed_body:
            self._parse_body()

        return self._forms

    @property
    def files(self):
        """Get the file data for the current request.

        Returns:
            dict[str, Any]: the file data
        """

        if not self.__parsed_body:
            self._parse_body()

        return self._files

    @property
    def json(self):
        """Get the JSON data for the current request.

        Returns:
            dict[str, Any]: the JSON data
        """

        if not self.__parsed_body:
            self._parse_body()

        return self._json

    @classmethod
    def bind(cls, environ: dict[str, Any]):
        """Bind the current request to the given environ.

        Args:
            environ (dict[str, Any]): the environ for the current request
        """

        cls._local.request = cls(environ)

    @classmethod
    def current(cls) -> Request:
        """Get the current request.

        Returns:
            Request: the current request
        """

        if not hasattr(cls._local, "request"):
            raise RuntimeError("No request bound to the current thread")
        return cls._local.request

    @classmethod
    def clear(cls):
        """
        Clear the current request.
        """

        if hasattr(cls._local, "request"):
            del cls._local.request


class LocalRequest:
    """
    A proxy object for accessing the current request.

    This object forwards all attribute access to the current request.
    """

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the current request."""
        return getattr(Request.current(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Forward attribute setting to the current request."""
        return setattr(Request.current(), name, value)

    def __repr__(self) -> str:
        """Return a string representation of the current request."""
        return repr(Request.current())


request = cast(Request, LocalRequest())
