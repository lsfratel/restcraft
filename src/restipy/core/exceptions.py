import typing as t


class RestiPyException(Exception):
    """Base exception class for errors."""


class HTTPException(RestiPyException):
    """Base exception class for HTTP errors."""

    __slots__ = ('message', 'status_code', 'headers', 'code')

    default_code: t.Union[int, str] = 'HTTP_EXCEPTION'
    default_status_code: int = 500

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
        self.headers = headers
        self.status_code = status_code or self.default_status_code
        self.code = code or self.default_code

    def get_response(self):
        return {'code': self.code, 'error': self.message}
