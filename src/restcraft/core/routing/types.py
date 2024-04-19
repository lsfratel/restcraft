import re
import typing as t
import uuid


class ParamType:
    """
    Defines the base class for parameter types used in the routing system.

    The `ParamType` class provides an abstract interface for validating and
    converting parameter values in the routing system. Concrete subclasses of
    `ParamType` must implement the `validate` and `convert` methods
    to handle the specific requirements of the parameter type.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern: str = r'(.+)'

    @classmethod
    def validate(cls, value: t.Any) -> bool: ...

    @classmethod
    def convert(cls, value: t.Any) -> t.Any: ...


class IntType(ParamType):
    """
    The `IntType` class validates that the input value is a valid integer
    string, and converts the input value to an integer. The regular expression
    used for validation matches one or more digits.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern = r'(\d+)'

    @classmethod
    def validate(cls, value):
        return bool(re.match(cls.pattern, value))

    @classmethod
    def convert(cls, value):
        if cls.validate(value):
            return int(value)

        raise ValueError(
            f"Provided value '{value}' is not a valid integer string."
        )


class FloatType(ParamType):
    """
    The `FloatType` class validates that the input value is a valid
    floating-point number string, and converts the input value to a float.
    The regular expression used for validation matches one or more digits, a
    decimal point, and one or more additional digits.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern = r'(\d+\.\d+)'

    @classmethod
    def validate(cls, value):
        return bool(re.match(cls.pattern, value))

    @classmethod
    def convert(cls, value):
        if cls.validate(value):
            return float(value)

        raise ValueError(
            f"Provided value '{value}' is not a valid float string."
        )


class StringType(ParamType):
    """
    The `StringType` class validates that the input value is a valid string,
    and converts the input value to a string. The regular expression used for
    validation matches one or more characters that are not forward slashes.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern = r'([^/]+)'

    @classmethod
    def validate(cls, value):
        return bool(re.match(cls.pattern, value))

    @classmethod
    def convert(cls, value):
        if cls.validate(value):
            return str(value)

        raise ValueError(f"Provided value '{value}' is not valid str.")


class SlugType(ParamType):
    """
    The `SlugType` class validates that the input value is a valid slug string,
    and converts the input value to a string. The regular expression used for
    validation matches one or more characters that are lowercase letters,
    digits, or hyphens.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern = r'([a-z0-9-]+)'

    @classmethod
    def validate(cls, value):
        return bool(re.match(cls.pattern, value))

    @classmethod
    def convert(cls, value):
        normalized_slug = re.sub(r'[ _]', '-', value.lower())

        if cls.validate(normalized_slug):
            return normalized_slug

        raise ValueError(
            f"Provided value '{value}' cannot be converted to a valid slug."
        )


class UUIDType(ParamType):
    """
    The `UUIDType` class validates that the input value is a valid UUID string,
    and converts the input value to a `uuid.UUID` object. The regular
    expression used for validation matches a string of 36 characters consisting
    of hexadecimal digits and hyphens.
    """

    """
    The pattern must be a capturing group. Otherwise, the route will
    not match.
    """
    pattern = r'([0-9a-fA-F-]{36})'

    @classmethod
    def validate(cls, value):
        return bool(re.match(cls.pattern, value))

    @classmethod
    def convert(cls, value):
        if cls.validate(value):
            return str(uuid.UUID(value))

        raise ValueError(
            f"Provided value '{value}' cannot be converted to a valid UUID."
        )
