import typing as t

__all__ = ('HTTPException',)


class RestCraftException(Exception):
    """Base exception class for errors."""

    default_status_code: int = 500
    default_message: str = 'Internal server error.'
    default_exception_code: str = 'INTERNAL_SERVER_ERROR'

    def __init__(
        self,
        message: t.Optional[str] = None,
        payload: t.Optional[t.Any] = None,
        status_code: t.Optional[int] = None,
        exception_code: t.Optional[str] = None,
        headers: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        self.payload = payload
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status_code
        self.exception_code = exception_code or self.default_exception_code
        self.headers = headers
        super().__init__(message or self.default_message)

    def to_response(self) -> t.Dict[str, t.Any]:
        """
        Returns a dictionary representation of the error response that can be
        used to generate the appropriate HTTP response.
        """
        return {
            'code': self.exception_code,
            'message': self.message,
            **(self.payload or {}),
        }

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.status_code} {self.message}>'


class HTTPException(RestCraftException):
    """
    An exception class for HTTP-related errors.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent various HTTP-related errors that may occur
    during the execution of the application.
    """

    default_status_code: int = 400
    default_message: str = 'An unknown error has occurred.'
    default_exception_code: str = 'HTTP_EXCEPTION'


class MalformedBody(RestCraftException):
    """
    An exception class for when the request body is malformed.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when the request body is not
    in the expected format.
    """

    default_status_code: int = 400
    default_message: str = 'Malformed body.'
    default_exception_code: str = 'MALFORMED_BODY'


class ImproperlyConfigured(RestCraftException):
    """
    An exception class for when the application is improperly configured.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when the application is not
    properly configured, such as missing required configuration values.
    """

    default_status_code: int = 500
    default_message: str = 'Improperly configured.'
    default_exception_code: str = 'IMPROPERLY_CONFIGURED'


class RequestBodyTooLarge(RestCraftException):
    """
    An exception class for when the request body is too large.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when the request body exceeds
    the maximum allowed size.
    """

    default_status_code: int = 413
    default_message: str = 'Request body too large.'
    default_exception_code: str = 'BODY_TOO_LARGE'


class InvalidStatusCode(RestCraftException):
    """
    An exception class for when an invalid status code is used.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when an invalid HTTP status
    code is used, such as a code that is out of the valid range or not
    supported by the application.
    """

    default_status_code: int = 500
    default_message: str = 'Invalid status code.'
    default_exception_code: str = 'INVALID_STATUS_CODE'


class FileNotFound(RestCraftException):
    """
    An exception class for when a file is not found.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when a requested file is not
    found on the server.
    """

    default_status_code: int = 404
    default_message: str = 'File not found.'
    default_exception_code: str = 'FILE_NOT_FOUND'


class UnsupportedBodyType(RestCraftException):
    """
    An exception class for when the request body has an unsupported type.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when the request body is of a
    type that is not supported by the application.
    """

    default_status_code: int = 500
    default_message: str = 'Unsupported body type.'
    default_exception_code: str = 'UNSUPPORTED_BODY_TYPE'


class RouteNotFound(RestCraftException):
    """
    An exception class for when a requested route is not found.

    This exception class inherits from the base `RestCraftException` class and
    provides default values for the status code, message, and exception code.

    It can be used to represent errors that occur when a client requests a
    route that is not defined or implemented in the application.
    """

    default_status_code: int = 404
    default_message: str = 'Route not found.'
    default_exception_code: str = 'ROUTE_NOT_FOUND'
