from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from ...core.application import RestCraft
    from ..routing.request import Request
    from ..routing.response import Response


class Middleware:
    """
    Middleware class for handling pre and post request processing.

    This class provides methods for performing actions before and after the
    route handler is executed. It can be used to modify the request or response
    objects, or to short-circuit the request processing by returning a
    response.

    Attributes:
        app (RestCraft): The RestCraft application instance.

    Methods:
        before_route(req: Request) -> Optional[Response]:
            Called before the route handler is executed.
        before_handler(req: Request) -> Optional[Response]:
            Called before the route handler is executed.
        after_handler(req: Request, res: Response) -> None:
            Called after the route handler is executed.
    """

    def __init__(self, app: RestCraft) -> None:
        self.app = app

    def before_route(self, req: Request) -> t.Optional[Response]:
        """
        Called before the route handler is executed.

        This method can be used to modify the request object or to
        short-circuit the request processing by returning a response.

        Args:
            req (Request): The request object.

        Returns:
            Optional[Response]: A response object to short-circuit the request
                processing, or None to continue processing the request.
        """
        ...

    def before_handler(self, req: Request) -> t.Optional[Response]:
        """
        Called before the route handler is executed.

        This method can be used to modify the request object or to
        short-circuit the request processing by returning a response.

        Args:
            req (Request): The request object.

        Returns:
            Optional[Response]: A response object to short-circuit the request
                processing, or None to continue processing the request.
        """
        ...

    def after_handler(self, req: Request, res: Response) -> None:
        """
        Called after the route handler is executed.

        This method can be used to modify the response object before it is
        sent to the client.

        Args:
            req (Request): The request object.
            res (Response): The response object.
        """
        ...

    def __repr__(self) -> str:
        """
        Returns a string representation of the class instance.

        This method is used to provide a human-readable string representation
        of the class instance, which is useful for debugging and logging
        purposes.

        Returns:
            str: A string representation of the class instance.
        """
        return f'<{self.__class__.__name__}>'
