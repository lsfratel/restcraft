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
        code: t.Optional[t.Union[int, str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.default_status_code
        self.headers = headers
        self.code = code or self.code

    def to_response(self):
        raise NotImplementedError


class InternalServerErrorException(BaseResponseException):
    code: t.Union[int, str] = 'INTERNAL_SERVER_ERROR'
    default_status_code: int = 500

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )


class RouteNotFoundException(BaseResponseException):
    code: t.Union[int, str] = 'NOT_FOUND'
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


class RequestBodyTooLargeException(BaseResponseException):
    code: t.Union[int, str] = 'BODY_TOO_LARGE'
    default_status_code: int = 413

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )
