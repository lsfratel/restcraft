from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from restcraft.exceptions import RestCraftException
from restcraft.http import JSONResponse, Request, Response, Router
from restcraft.plugin import PluginManager

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from types import ModuleType
    from typing import Any

    from restcraft.plugin import Plugin


class RestCraft:
    def __init__(self, config: ModuleType) -> None:
        self.router = Router()
        self.config = config
        self.exceptions: dict[type[Exception], Callable] = {}
        self.plugin_manager = PluginManager(self)

        self.register_exception(Exception)(self._default_exception_handler)

    def register_router(self, router: Router):
        self.router.merge(router)

    def register_exception(self, exc: type[Exception]):
        def wrapper(func: Callable[..., Response]):
            self.exceptions[exc] = func
            return func

        return wrapper

    def register_plugin(self, plugin: Plugin):
        self.plugin_manager.register(plugin)

    def unregister_plugin(self, plugin: Plugin | str):
        self.plugin_manager.unregister(plugin)

    def __call__(
        self, environ: dict[str, Any], start_response: Callable
    ) -> Iterable[bytes]:
        environ["wsgi.application"] = self
        Request.bind(environ)
        req_path = environ.get("PATH_INFO", "/")
        req_method = environ.get("REQUEST_METHOD", "GET")

        try:
            dispatcher = self.plugin_manager.before_route(self.router.dispatch)
            if isinstance(dispatcher, Response):
                response = dispatcher
            else:
                handler, metadata, params = dispatcher(req_method, req_path)
                handler = self.plugin_manager.before_handler(handler, metadata)
                if isinstance(handler, Response):
                    response = handler
                else:
                    response = handler(**(params or {}))
            if not isinstance(response, Response):
                raise TypeError("Handler must return a Response object.")
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
