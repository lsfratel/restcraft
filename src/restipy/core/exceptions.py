import typing as t


class RestiPyException(Exception):
    """Base exception class for errors."""


class HTTPException(RestiPyException):
    """Base exception class for HTTP errors.

    Attributes:
        message (str): The error message.
        status_code (int): The HTTP status code associated with the error.
        headers (dict): The headers to be included in the error response.
        code (Union[int, str]): The error code associated with the error.
        error (Any): Additional error information.

    Methods:
        get_response(): Returns the error response body.
    """

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
        """
        Initialize a new instance of the Exception class.

        Args:
            message (str): The error message.
            status_code (int, optional): The HTTP status code associated with
                the exception. Defaults to None.
            headers (dict, optional): Additional headers to be included in the
                response. Defaults to {}.
            error (Any, optional): The underlying error object. Defaults to
                None.
            code (Union[int, str], optional): A custom error code. Defaults to
                None.
        """
        super().__init__(message)
        self.message = message
        self.headers = headers
        self.status_code = status_code or self.default_status_code
        self.code = code or self.default_code
        self.error = error

    def get_response(self):
        """Returns the error response body.

        Returns:
            dict: The error response body.
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
            str: A string representation of the HTTPException object.
        """
        return f'<HTTPException {self.code!r} {self.message!r}>'
