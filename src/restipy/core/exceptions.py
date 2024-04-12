import typing as t


class RestiPyException(Exception):
    """Base exception class for errors."""


class HTTPException(RestiPyException):
    """Base exception class for HTTP errors."""

    __slots__ = ('message', 'status_code', 'headers', 'code', 'error')

    default_code: t.Union[int, str] = 'HTTP_EXCEPTION'
    default_status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        status_code: t.Optional[int] = None,
        headers: dict = {},
        error: t.Optional[t.Any] = None,
        code: t.Optional[t.Union[int, str]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.headers = headers
        self.status_code = status_code or self.default_status_code
        self.code = code or self.default_code
        self.error = error

    def get_response(self):
        body = {'code': self.code, 'message': self.message}

        if self.error:
            body['error'] = self.error

        return body

    def __repr__(self) -> str:
        return f'<HTTPException {self.code!r} {self.message!r}>'
