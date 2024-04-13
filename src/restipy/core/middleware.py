from restipy.core.request import Request
from restipy.core.response import Response


class BaseMiddleware:
    """
    The `BaseMiddleware` class provides a base implementation for middleware
    in the Restipy framework. Middleware is used to intercept and modify
    requests and responses before and after they are handled by the
    application.

    The `before_route` method is called before the request is routed to the
    appropriate handler. This method can return a `Response` object to
    short-circuit the request processing, or `None` to allow the request to
    continue.

    The `before_handler` method is called before the request handler is
    executed. This method can also return a `Response` object to short-circuit
    the request processing, or `None` to allow the request to continue.

    The `after_handler` method is called after the request handler has been
    executed. This method can be used to perform post-processing on the
    response, such as adding headers or modifying the response body.
    """

    def before_route(self, req: Request) -> Response | None:
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

    def before_handler(self, req: Request) -> Response | None:
        """
        This method is called before the request handler is executed.

        Args:
            `req (Request):` The incoming request object.

        Returns:
            `Response | None:` The response object or None if no response
                is generated.
        """
        pass

    def after_handler(self, req: Request, res: Response):
        """
        This method is called after the request handler has been executed.

        Args:
            `req (Request):` The request object.
            `res (Response):` The response object.
        """
        pass
