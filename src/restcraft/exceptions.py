from typing import Any


class RestCraftException(Exception):
    def __init__(
        self,
        message: str = "Internal Server Error",
        *,
        status: int = 500,
        errors: dict[str, Any] = {},
    ):
        super().__init__(message, status, errors)
        self.message = message
        self.status = status
        self.errors = errors

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class MethodNotAllowedException(RestCraftException):
    def __init__(
        self,
        message: str = "The request method is not allowed",
        *,
        status: int = 405,
        errors: dict[str, Any] = {},
    ):
        super().__init__(message, status=status, errors=errors)


class NotFoundException(RestCraftException):
    def __init__(
        self,
        message="The requested resource was not found",
        *,
        status: int = 404,
        errors: dict[str, Any] = {},
    ):
        super().__init__(message, status=status, errors=errors)


class BodyException(RestCraftException):
    pass
