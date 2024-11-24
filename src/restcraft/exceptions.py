from typing import Any


class RestCraftException(Exception):
    def __init__(self, message: str, *, status: int = 500, errors: dict[str, Any] = {}):
        super().__init__(message, status, errors)
        self.message = message
        self.status = status
        self.errors = errors

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class MethodNotAllowedException(RestCraftException):
    pass


class NotFoundException(RestCraftException):
    pass


class BodyException(RestCraftException):
    pass
