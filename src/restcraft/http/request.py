from __future__ import annotations

import json
import threading
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import parse_qs

if TYPE_CHECKING:
    from restcraft.restcraft import RestCraft

from restcraft.contrib.http import MultipartParser
from restcraft.exceptions import RestCraftException


class Request:
    _local = threading.local()
    # __slots__ = (
    #     "ENV",
    #     "_query",
    #     "_forms",
    #     "_files",
    #     "_json",
    #     "_headers",
    #     "__parsed_query",
    #     "__parsed_body",
    # )

    def __init__(self, environ: dict[str, Any]):
        self.ENV = environ
        self._query: dict[str, Any] = {}
        self._forms: dict[str, Any] = {}
        self._files: dict[str, Any] = {}
        self._json: dict[str, Any] = {}
        self._headers: dict[str, str] = {}

    def _max_body_size(self):
        return int(getattr(self.app.config, "MAX_BODY_SIZE", 10 * 1024 * 1024))

    def _parse_body(self):
        if getattr(self, "__parsed_body", False):
            return

        setattr(self, "__parsed_body", True)

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
                self._json = json.loads(data.decode("utf-8"))
            elif ctype == "application/x-www-form-urlencoded":
                stream = self.ENV["wsgi.input"]
                self._forms = {
                    k: v[0] if len(v) == 1 else v
                    for k, v in parse_qs(stream.read(clength).decode("utf-8")).items()
                }
            elif ctype == "multipart/form-data":
                parser = MultipartParser(self.ENV, max_body_size=self._max_body_size())
                forms, files = parser.parse()

                self._forms = {k: v[0] if len(v) == 1 else v for k, v in forms.items()}
                self._files = {k: v[0] if len(v) == 1 else v for k, v in files.items()}
        except RestCraftException:
            raise
        except Exception as e:
            message = "Failed to parse request body"
            errors = {"description": str(e)}
            raise RestCraftException(message, errors=errors, status=400) from e

    @property
    def app(self) -> RestCraft:
        return self.ENV["wsgi.application"]

    @property
    def method(self):
        return self.ENV.get("REQUEST_METHOD", "GET").upper()

    @property
    def headers(self):
        if self._headers:
            return self._headers

        for k, v in self.ENV.items():
            if k.startswith("HTTP_"):
                self._headers[k[5:].replace("_", "-").lower()] = cast(str, v)

            if k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                self._headers[k.replace("_", "-").lower()] = cast(str, v)

        return self._headers

    @property
    def is_secure(self):
        return self.ENV.get("wsgi.url_scheme", "http") == "https"

    @property
    def path(self) -> str:
        return self.ENV.get("PATH_INFO", "/")

    @property
    def content_type(self) -> str:
        return self.ENV.get("CONTENT_TYPE", "")

    @property
    def content_length(self) -> int:
        return int(self.ENV.get("CONTENT_LENGTH", 0))

    @property
    def query(self):
        if getattr(self, "__parsed_query", False):
            return self._query

        setattr(self, "__parsed_query", True)

        qs: str = self.ENV.get("QUERY_STRING", "")

        if not qs:
            return self._query

        self._query = {
            k: v[0] if len(v) == 1 else v
            for k, v in parse_qs(qs, keep_blank_values=True).items()
        }

        return self._query

    @property
    def forms(self):
        if not getattr(self, "__parsed_body", False):
            self._parse_body()

        return self._forms

    @property
    def files(self):
        if not getattr(self, "__parsed_body", False):
            self._parse_body()

        return self._files

    @property
    def json(self):
        if not getattr(self, "__parsed_body", False):
            self._parse_body()

        return self._json

    @classmethod
    def bind(cls, environ: dict[str, Any]):
        cls._local.request = cls(environ)

    @classmethod
    def current(cls) -> Request:
        if not hasattr(cls._local, "request"):
            raise RuntimeError("No request bound to the current thread")
        return cls._local.request

    @classmethod
    def clear(cls):
        if hasattr(cls._local, "request"):
            del cls._local.request


class LocalRequest:
    def __getattr__(self, name: str):
        return getattr(Request.current(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        return setattr(Request.current(), name, value)

    def __repr__(self) -> str:
        return repr(Request.current())


request = cast(Request, LocalRequest())
