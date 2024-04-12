from restipy.core.request import Request
from restipy.core.response import Response


class BaseMiddleware:
    """Base middleware class for middlewares."""

    def before_route(self, req: Request) -> Response | None:
        pass

    def before_handler(self, req: Request) -> Response | None:
        pass

    def after_handler(self, req: Request, res: Response):
        pass
