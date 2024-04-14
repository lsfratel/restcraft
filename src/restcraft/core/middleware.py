from __future__ import annotations

import typing as t

from restcraft.core.request import Request
from restcraft.core.response import Response

if t.TYPE_CHECKING:
    from restcraft.core.application import RestCraft


class Middleware:
    """
    Represents a middleware component that can be used to intercept and modify
    requests and responses in a RestCraft application.

    The `Middleware` class provides three main methods that can be overridden
    to implement custom middleware functionality:

    - `before_route(self, req: Request) -> Response | None:` This method is
      called before routing the request to the appropriate route handler. It
      can be used to perform tasks such as authentication, authorization, or
      request transformation.

    - `before_handler(self, req: Request) -> Response | None:` This method is
      called before the request handler is executed. It can be used to perform
      tasks such as logging, metrics collection, or request validation.

    - `after_handler(self, req: Request, res: Response):` This method is called
      after the request handler has been executed. It can be used to perform
      tasks such as response transformation, caching, or error handling.

    Middleware components can be registered with a `RestCraft` application
    instance to customize the request/response processing pipeline.
    """

    def __init__(self, app: RestCraft) -> None:
        """
        Initializes a new instance of the `Middleware` class with the provided
        `RestCraft` application.

        Args:
            `app (RestCraft):` The `RestCraft` application instance that this
                middleware will be associated with.
        """
        self.app = app

    def before_route(self, req: Request) -> t.Optional[Response]:
        """
        This method is called before routing the request to the appropriate
        route handler.

        Args:
            `req (Request):` The incoming request object.

        Returns:
            `Response | None:` The response object if the middleware handles
                the request, None otherwise.
        """
        pass

    def before_handler(self, req: Request) -> t.Optional[Response]:
        """
        This method is called before the request handler is executed.

        Args:
            `req (Request):` The incoming request object.

        Returns:
            `Response | None:` The response object or None if no response
                is generated.
        """
        pass

    def after_handler(self, req: Request, res: Response) -> None:
        """
        This method is called after the request handler has been executed.

        Args:
            `req (Request):` The request object.
            `res (Response):` The response object.
        """
        pass

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'
