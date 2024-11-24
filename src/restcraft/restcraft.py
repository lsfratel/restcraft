from __future__ import annotations

import traceback
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import TYPE_CHECKING, Any

from restcraft.exceptions import RestCraftException
from restcraft.http import JSONResponse, Request, Router

if TYPE_CHECKING:
    from restcraft.http import Response
    from restcraft.plugin import Plugin


_not_found_error = RestCraftException("Resource not found", status=404)
_method_not_allowed = RestCraftException("Method not allowed", status=405)


class RestCraft:
    def __init__(self, config: ModuleType) -> None:
        self.router = Router()
        self.config = config
        self.exceptions: dict[type[Exception], Callable] = {}
        self.plugins: list[Plugin] = []

        self.register_exception(Exception)(self._default_exception_handler)

    def register_router(self, router: Router):
        self.router.merge(router)
        for plugin in self.plugins:
            self.router.cache_plugin(plugin)

    def register_exception(self, exc: type[Exception]):
        def wrapper(func: Callable[..., Response]):
            self.exceptions[exc] = func
            return func

        return wrapper

    def register_plugin(self, plugin: Plugin):
        plugin.setup(self)
        self.plugins.append(plugin)
        self.router.cache_plugin(plugin)

    def __call__(
        self, environ: dict[str, Any], start_response: Callable
    ) -> Iterable[bytes]:
        environ["wsgi.application"] = self
        Request.bind(environ)
        req_path = environ.get("PATH_INFO", "/")
        req_method = environ.get("REQUEST_METHOD", "GET")

        try:
            router_node, params = self.router.find(req_path)
            if not router_node:
                raise _not_found_error

            if req_method not in router_node.handlers:
                raise _method_not_allowed

            handler = router_node.handlers[req_method]["handler"]

            response = handler(**(params or {}))
        except Exception as e:
            response = self._handle_exception(environ, e)
        finally:
            Request.clear()

        status, headers, body = response.to_wsgi()

        start_response(status, headers)

        if req_method == "HEAD":
            return []

        return [body]

    def _handle_exception(self, environ: dict[str, Any], exc: Exception) -> Response:
        handler = self.exceptions.get(type(exc), self.exceptions[Exception])
        response = handler(exc)

        if not isinstance(exc, RestCraftException):
            environ["wsgi.errors"].write(traceback.format_exc())
            environ["wsgi.errors"].flush()

        return response

    def _default_exception_handler(self, exc: Exception) -> Response:
        if isinstance(exc, RestCraftException):
            body = {"details": exc.message}
            if exc.errors:
                body = {"details": exc.message, "errors": exc.errors}
            return JSONResponse(body, status=exc.status)
        return JSONResponse({"details": "Internal Server Error"}, status=500)
