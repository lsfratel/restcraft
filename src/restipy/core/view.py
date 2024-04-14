from __future__ import annotations

import typing as t

from restipy.core.request import Request
from restipy.core.response import Response

if t.TYPE_CHECKING:
    from restipy.core.application import RestiPy


__all__ = ('View',)


class View:
    """
    The `View` class is the base class for all views in the Restipy
    framework. It provides a set of methods that can be overridden by
    subclasses to handle different aspects of the request/response lifecycle.

    The `before_handler` method is called before the request handler is
    executed, and can be used for pre-processing the request.

    The `after_handler` method is called after the request handler is
    executed, and can be used for post-processing the response.

    The `handler` method is the main request handler that must be implemented
    by subclasses. It takes a `Request` object and returns a `Response` object.

    The `on_exception` method is called when an exception is raised during
    request handling. It can be used to handle specific exceptions and return
    custom responses.
    """

    __slots__ = ('route', 'methods', 'app')

    route: t.Union[str, t.Pattern[str]]
    methods: t.List[str]

    def __init__(self, app: RestiPy) -> None:
        """
        Initializes a new instance of the `View` class.
        """
        self.app = app

    def before_handler(self, req: Request) -> t.Optional[Response]:
        """
        Method called before the request handler is executed.

        It can be used for pre-processing the request.

        Returns:
            `Response | None:` The response object or None if no response
                is generated.
        """
        ...

    def after_handler(
        self, req: Request, res: Response
    ) -> t.Optional[Response]:
        """
        Method called after the request handler is executed.

        It can be used for post-processing the response.

        Returns:
            `Response | None:` The response object or None if no response
                is generated.
        """
        ...

    def handler(self, req: Request) -> Response:
        """
        Method that handles the incoming request.

        This method needs to be implemented by subclasses.

        Returns:
            `Response:` The response object.
        """
        ...

    def on_exception(self, req: Request, exc: Exception) -> Response:
        """
        Method called when an exception is raised during request handling.

        It can be used to handle specific exceptions and return custom
        responses.

        Returns:
            `Response:` The response object.
        """
        raise exc

    def __repr__(self) -> str:
        """
        Returns a string representation of the View instance.
        """
        return f'<{self.__class__.__name__} {self.methods} {self.route}>'
