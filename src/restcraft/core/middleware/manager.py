from __future__ import annotations

import typing as t

from ..routing.response import Response

if t.TYPE_CHECKING:
    from ..routing.request import Request
    from .middleware import Middleware


class MiddlewareManager:
    """
    The `MiddlewareManager` class is responsible for managing a collection of
    middleware components that can be applied to incoming requests and outgoing
    responses.

    The `MiddlewareManager` provides methods to add middleware components, and
    to invoke the `before_route`, `before_handler`, and `after_handler` methods
    on each middleware component during the request/response lifecycle.
    """

    def __init__(self) -> None:
        self._middlewares: t.List[Middleware] = []

    def add_middleware(self, middleware: Middleware) -> None:
        self._middlewares.append(middleware)

    def before_route(self, req: Request) -> t.Optional[Response]:
        for middleware in self._middlewares:
            res = middleware.before_route(req)
            if isinstance(res, Response):
                return res

    def before_handler(self, req: Request) -> t.Optional[Response]:
        for middleware in self._middlewares:
            res = middleware.before_handler(req)
            if isinstance(res, Response):
                return res

    def after_handler(self, req: Request, res: Response) -> None:
        for middleware in self._middlewares:
            middleware.after_handler(req, res)


middleware_manager = MiddlewareManager()
