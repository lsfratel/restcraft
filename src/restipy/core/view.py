import typing as t

from restipy.core.exceptions import HTTPException
from restipy.core.request import Request
from restipy.core.response import Response


class BaseView:
    """
    Base class for views in the REST framework.
    """

    __slots__ = ('route', 'methods')

    route: str
    methods: list[str]

    def before(self, req: Request) -> t.Optional[Response]:
        """
        Method called before the request handler is executed.
        It can be used for pre-processing the request.
        """
        pass

    def after(self, req: Request, res: Response) -> t.Optional[Response]:
        """
        Method called after the request handler is executed.
        It can be used for post-processing the response.
        """
        pass

    def handler(self, req: Request) -> Response:
        """
        Method that handles the incoming request.
        This method needs to be implemented by subclasses.
        """
        raise NotImplementedError

    def on_exception(self, req: Request, exc: Exception) -> Response:
        """
        Method called when an exception is raised during request handling.

        It can be used to handle specific exceptions and return custom
        responses.
        """
        if isinstance(exc, HTTPException):
            return Response(
                exc.get_response(),
                status_code=exc.status_code,
                headers=exc.headers,
            )
        return Response(
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'error': 'Something went wrong, try again later.',
            },
            status_code=500,
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the BaseView instance.
        """
        return f'<{self.__class__.__name__} {self.route} {self.methods}>'
