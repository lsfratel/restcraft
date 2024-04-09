import typing as t

from restipy.core.response import Response


class RestiPyException(Exception):
    """Base exception class for RestiPy errors."""


class BaseResponseException(RestiPyException):
    code: t.Union[int, str] = 'BASE_RESPONSE_EXCEPTION'
    default_status_code: int = 400

    def __init__(
        self,
        message: str,
        *,
        headers: dict = {},
        status_code: t.Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.default_status_code
        self.headers = headers

    def to_response(self):
        raise NotImplementedError


class InternalServerError(BaseResponseException):
    code: t.Union[int, str] = 'INTERNAL_SERVER_ERROR'
    default_status_code: int = 500

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )


class RouteNotFoundException(BaseResponseException):
    code: t.Union[int, str] = 'ROUTE_NOT_FOUND'
    default_status_code: int = 404

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )


class MalformedBodyException(BaseResponseException):
    code: t.Union[int, str] = 'MALFORMED_BODY'
    default_status_code: int = 400

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )
