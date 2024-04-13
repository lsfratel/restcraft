from restipy.core.request import Request
from restipy.core.response import Response


class BaseMiddleware:
    """Base middleware class for middlewares.

    This class serves as the base class for implementing middlewares in the
    Restipy framework.
    Middlewares are components that can intercept and modify requests and
    responses before and after they are handled by theapplication.

    Attributes:
        None

    Methods:
        before_route: Called before the request is routed to a handler.
            It can modify the request or return a response.
        before_handler: Called before the request is handled by a handler.
            It can modify the request or return a response.
        after_handler: Called after the request is handled by a handler.
            It can modify the request or response.
    """

    def before_route(self, req: Request) -> Response | None:
        """
        This method is called before routing the request to the appropriate
        route handler.

        Args:
            req (Request): The incoming request object.

        Returns:
            Response | None: The response object if the middleware handles the
                request, None otherwise.
        """
        pass

    def before_handler(self, req: Request) -> Response | None:
        """
        This method is called before the request handler is executed.

        Args:
            req (Request): The incoming request object.

        Returns:
            Response | None: The response object or None if no response
                is generated.
        """
        pass

    def after_handler(self, req: Request, res: Response):
        """
        This method is called after the request handler has been executed.

        Args:
            req (Request): The request object.
            res (Response): The response object.
        """
        pass
