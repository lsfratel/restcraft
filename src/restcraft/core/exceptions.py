import typing as t

__all__ = (
    'HTTPException',
    'RestCraftException',
)


class RestCraftException(Exception):
    """
    Base class for RestCraft exceptions.

    Args:
        body (Any): The body of the exception.
        status_code (int, optional): The HTTP status code of the exception.
            Defaults to 500.
        headers (Optional[Dict[str, str]], optional): The headers of the
            exception. Defaults to None.

    Attributes:
        body (Any): The body of the exception.
        status_code (int): The HTTP status code of the exception.
        headers (Optional[Dict[str, str]]): The headers of the exception.
    """

    def __init__(
        self,
        body: t.Any,
        status_code: int = 500,
        headers: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        self.body = body
        self.status_code = status_code
        self.headers = headers
        super().__init__(body)

    def __repr__(self) -> str:
        """
        Return a string representation of the exception.

        Returns:
            str: The string representation of the exception.
        """
        return f'<{self.__class__.__name__} {self.status_code}>'


class HTTPException(RestCraftException):
    """
    Exception class for HTTP errors.

    This class is a subclass of RestCraftException and does not introduce
    any specific attributes or methods. It is provided as a convenience
    class for raising HTTP errors.

    Args:
        body (Any): The body of the exception.
        status_code (int, optional): The HTTP status code of the exception.
            Defaults to 500.
        exception_code (Union[str, int], optional): The exception code.
            Defaults to 'INTERNAL_SERVER_ERROR'.
        headers (Optional[Dict[str, str]], optional): The headers of the
            exception. Defaults to None.

    Attributes:
        body (Any): The body of the exception.
        status_code (int): The HTTP status code of the exception.
        exception_code (Union[str, int]): The exception code.
        headers (Optional[Dict[str, str]]): The headers of the exception.
    """
