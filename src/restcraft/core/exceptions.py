import typing as t

__all__ = ('HTTPException',)


class RestCraftException(Exception):
    """
    Defines a base exception class for RestCraft, which provides a standard
    way to handle and report exceptions in the application.

    The `RestCraftException` class provides the following features:

    - Defines default values for the status code, message, and exception code.
    - Allows overriding the default values when creating an instance of the
      exception.
    - Provides a `to_response()` method to convert the exception to a response
      dictionary, which includes the exception code, message, and any
      additional payload data.
    - Provides a human-readable string representation of the exception.
    """

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
        Converts the exception to a response dictionary.

        The response dictionary includes the exception code, message, and any
        additional payload data.

        Returns:
            dict: A dictionary containing the exception code, message,
                and payload.
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
    HTTP exception base class.

    This exception class is used as a base for all HTTP-related exceptions. It
    provides default values for the status code, message, and exception code.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 400.
        default_message: The default error message for this exception, which
            is 'An unknown error has occurred.'.
        default_exception_code: The default exception code for this exception,
            which is 'HTTP_EXCEPTION'.
    """

    default_status_code: int = 400
    default_message: str = 'An unknown error has occurred.'
    default_exception_code: str = 'HTTP_EXCEPTION'


class MalformedBody(RestCraftException):
    """
    Exception class for a malformed request body.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 400.
        default_message: The default error message for this exception, which
            is 'Malformed body.'.
        default_exception_code: The default exception code for this exception,
            which is 'MALFORMED_BODY'.
    """

    default_status_code: int = 400
    default_message: str = 'Malformed body.'
    default_exception_code: str = 'MALFORMED_BODY'


class ImproperlyConfigured(RestCraftException):
    """
    Exception class for an improperly configured application.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 500.
        default_message: The default error message for this exception, which
            is 'Improperly configured.'.
        default_exception_code: The default exception code for this exception,
            which is 'IMPROPERLY_CONFIGURED'.
    """

    default_status_code: int = 500
    default_message: str = 'Improperly configured.'
    default_exception_code: str = 'IMPROPERLY_CONFIGURED'


class RequestBodyTooLarge(RestCraftException):
    """
    Exception class for a request body that is too large.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 413.
        default_message: The default error message for this exception, which
            is 'Request body too large.'.
        default_exception_code: The default exception code for this exception,
            which is 'BODY_TOO_LARGE'.
    """

    default_status_code: int = 413
    default_message: str = 'Request body too large.'
    default_exception_code: str = 'BODY_TOO_LARGE'


class InvalidStatusCode(RestCraftException):
    """
    Exception class for an invalid status code.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 500.
        default_message: The default error message for this exception, which
            is 'Invalid status code.'.
        default_exception_code: The default exception code for this exception,
            which is 'INVALID_STATUS_CODE'.
    """

    default_status_code: int = 500
    default_message: str = 'Invalid status code.'
    default_exception_code: str = 'INVALID_STATUS_CODE'


class FileNotFound(RestCraftException):
    """
    Exception class for a file that was not found.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 404.
        default_message: The default error message for this exception, which
            is 'File not found.'.
        default_exception_code: The default exception code for this exception,
            which is 'FILE_NOT_FOUND'.
    """

    default_status_code: int = 404
    default_message: str = 'File not found.'
    default_exception_code: str = 'FILE_NOT_FOUND'


class UnsupportedBodyType(RestCraftException):
    """
    Exception class for an unsupported body type.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 500.
        default_message: The default error message for this exception, which
            is 'Unsupported body type.'.
        default_exception_code: The default exception code for this exception,
            which is 'UNSUPPORTED_BODY_TYPE'.
    """

    default_status_code: int = 500
    default_message: str = 'Unsupported body type.'
    default_exception_code: str = 'UNSUPPORTED_BODY_TYPE'


class RouteNotFound(RestCraftException):
    """
    Exception class for a route that was not found.

    Attributes:
        default_status_code: The default HTTP status code for this exception,
            which is 404.
        default_message: The default error message for this exception, which
            is 'Route not found.'.
        default_exception_code: The default exception code for this exception,
            which is 'ROUTE_NOT_FOUND'.
    """

    default_status_code: int = 404
    default_message: str = 'Route not found.'
    default_exception_code: str = 'ROUTE_NOT_FOUND'
