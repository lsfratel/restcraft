from __future__ import annotations

import typing as t

from restcraft.core.request import Request
from restcraft.core.response import Response

if t.TYPE_CHECKING:
    from restcraft.core.application import RestCraft


__all__ = ('View',)


class View:
    """
    Represents a view in the RestCraft framework.

    Attributes:
        route (Union[str, Pattern[str]]): The route associated with the view.
        methods (List[str]): The HTTP methods supported by the view.
        app (RestCraft): The RestCraft application instance.

    Methods:
        __init__(self, app: RestCraft) -> None: Initializes a new instance of
            the View class.
        before_handler(self, req: Request) -> Optional[Response]: Executes
            before the request handler.
        after_handler(self, req: Request, res: Response) -> Optional[Response]:
            Executes after the request handler.
        handler(self, req: Request) -> Response: Handles the incoming request.
        on_exception(self, req: Request, exc: Exception) -> Response: Handles
            exceptions raised during request handling.
    """

    __slots__ = ('route', 'methods', 'app')

    route: t.Union[str, t.Pattern[str]]
    methods: t.List[str]

    def __init__(self, app: RestCraft) -> None:
        """
        Initializes a new instance of the View class.

        Args:
            app (RestCraft): The RestCraft application instance.
        """
        self.app = app

    def before_handler(self, req: Request) -> t.Optional[Response]:
        """
        Executes before the request handler.

        Args:
            req (Request): The incoming request.

        Returns:
            Optional[Response]: The response to be sent back, or None if no
                response is generated.
        """
        ...

    def after_handler(
        self, req: Request, res: Response
    ) -> t.Optional[Response]:
        """
        Executes after the request handler.

        Args:
            req (Request): The incoming request.
            res (Response): The response generated by the request handler.

        Returns:
            Optional[Response]: The response to be sent back, or None if no
                response is generated.
        """
        ...

    def handler(self, req: Request) -> Response:
        """
        Handles the incoming request.

        Args:
            req (Request): The incoming request.

        Returns:
            Response: The response generated by the request handler.
        """
        ...

    def on_exception(self, req: Request, exc: Exception) -> Response:
        """
        Handles exceptions raised during request handling.

        Args:
            req (Request): The incoming request.
            exc (Exception): The exception raised during request handling.

        Returns:
            Response: The response to be sent back.
        """
        raise exc

    def __repr__(self) -> str:
        """
        Returns a string representation of the View instance.

        Returns:
            str: The string representation of the View instance.
        """
        return f'<{self.__class__.__name__} {self.methods} {self.route}>'