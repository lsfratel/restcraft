from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from restcraft.http.request import request
from restcraft.http.response import Response
from restcraft.plugin import Plugin


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

    def before_route(
        self, dispatcher: Callable[..., tuple]
    ) -> Callable[..., tuple] | Response:
        """
        Modifies or wraps the route dispatcher.

        This method is called before the application's route is dispatched.

        Args:
            dispatcher (Callable[..., tuple]): The route dispatcher.

        Returns:
            Callable[..., tuple] | Response: The modified route dispatcher
            or a Response object if the plugin wants to short-circuit the request.
        """

        if request.method == "OPTIONS":
            return Response(
                status=204, headers=self._build_headers(origin=request.origin)
            )

        return super().before_route(dispatcher)

    def _build_headers(self, origin: None | str = None):
        """
        Builds the CORS response headers.

        Args:
            origin (None | str): The value for the Access-Control-Allow-Origin header.
                If None, the value is set to the list of allow_origins joined by a comma
                and a space.

        Returns:
            dict[str, str]: The CORS response headers.
        """

        headers = {
            "Access-Control-Allow-Origin": origin or ", ".join(self.allow_origins),
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
        }

        if self.allow_headers:
            headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        if self.max_age is not None:
            headers["Access-Control-Max-Age"] = str(self.max_age)

        return headers
