import typing as t

__all__ = ('HTTPException', 'RestiPyException')


class RestiPyException(Exception):
    """Base exception class for errors."""


class HTTPException(RestiPyException):
    """
    Represents an HTTP exception that can be raised by the application.

    The `HTTPException` class is a custom exception that can be raised when an
    HTTP-related error occurs in the application. It provides a standardized
    way to handle and report these errors, including the ability to specify the
    HTTP status code, error message, headers, and an optional underlying error
    object.

    The `get_response()` method returns a dictionary representation of the
    error response that can be used to generate the appropriate HTTP response.
    """

    __slots__ = ('message', 'status_code', 'headers', 'code', 'error')

    default_code: t.Union[int, str] = 'HTTP_EXCEPTION'
    default_status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        status_code: t.Optional[int] = None,
        headers: t.Dict = {},
        error: t.Optional[t.Any] = None,
        code: t.Optional[t.Union[int, str]] = None,
    ) -> None:
        """
        Initialize a new instance of the Exception class.

        Args:
            `message (str):` The error message.
            `status_code (int, optional):` The HTTP status code associated with
                the exception. Defaults to None.
            `headers (dict, optional):` Additional headers to be included in
                the response. Defaults to {}.
            `error (Any, optional):` The underlying error object. Defaults to
                None.
            `code (Union[int, str], optional):` A custom error code. Defaults
                to None.
        """
        super().__init__(message)
        self.message = message
        self.headers = headers
        self.status_code = status_code or self.default_status_code
        self.code = code or self.default_code
        self.error = error

    def get_response(self) -> t.Dict[str, t.Any]:
        """Returns the error response body.

        Returns:
            `dict:` The error response body.
        """
        body = {'code': self.code, 'message': self.message}

        if self.error:
            body['error'] = self.error

        return body

    def __repr__(self) -> str:
        """
        Returns a string representation of the HTTPException object.

        The string representation includes the HTTP status code and the
        error message.

        Returns:
            `str:` A string representation of the HTTPException object.
        """
        return f'<HTTPException {self.code!r} {self.message!r}>'
