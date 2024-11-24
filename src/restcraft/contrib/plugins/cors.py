from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from restcraft.restcraft import RestCraft

from restcraft.http.request import request
from restcraft.http.response import Response
from restcraft.plugin import Plugin, PluginException


class CORSPlugin(Plugin):
    name = "cors_plugin"

    def __init__(
        self,
        allow_origins: list[str] = ["*"],
        allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers: list[str] | None = None,
        allow_credentials: bool = False,
        max_age: int | None = None,
    ):
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def setup(self, app: RestCraft):
        if any(isinstance(plugin, CORSPlugin) for plugin in app.plugins):
            raise PluginException("CORS plugin already installed")

    def apply(
        self,
        callback: Callable[..., Response],
        metadata: dict[str, Any],
    ):
        methods = metadata.get("methods", self.allow_methods)

        def wrapper(*args, **kwargs):
            method = request.method
            print(method)

            if method == "OPTIONS":
                return Response(
                    status=204, headers=self._build_headers(methods=methods)
                )

            origin = request.ENV.get("HTTP_ORIGIN")

            if origin and (origin in self.allow_origins or "*" in self.allow_origins):
                headers = self._build_headers(origin, methods=methods)
            else:
                headers = self._build_headers(methods=methods)

            response = callback(*args, **kwargs)

            for key, value in headers.items():
                response.headers[key] = value

            return response

        return wrapper

    def _build_headers(
        self, origin: None | str = None, methods: None | list[str] = None
    ):
        headers = {
            "Access-Control-Allow-Origin": origin or ", ".join(self.allow_origins),
            "Access-Control-Allow-Methods": ", ".join(methods or self.allow_methods),
        }

        if self.allow_headers:
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        if self.max_age is not None:
            headers["Access-Control-Max-Age"] = str(self.max_age)

        return headers
