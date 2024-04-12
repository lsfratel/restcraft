import typing as t

from restipy.core.request import Request
from restipy.core.response import Response


class BaseView:
    __slots__ = ('route', 'methods')

    route: str
    methods: list[str]

    def before(self, req: Request) -> t.Optional[Response]:
        pass

    def after(self, req: Request, res: Response) -> t.Optional[Response]:
        pass

    def handler(self, req: Request) -> Response:
        raise NotImplementedError

    def on_exception(self, req: Request, exc: Exception) -> Response:
        return Response(
            body={'error': 'Internal Server Error.'}, status_code=500
        )
