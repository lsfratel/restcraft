from __future__ import annotations

import typing as t

from .context import ThreadSafeContext

if t.TYPE_CHECKING:
    from ..core import Request


def pep3333(value: str, errors='strict') -> str:
    """
    Convert the given value to a string using the PEP 3333 encoding rules.

    Args:
        value (str): The value to be converted.
        errors (str, optional): The error handling scheme to use for encoding
            errors. Defaults to 'strict'.

    Returns:
        str: The converted string.
    """
    return str(value).encode('latin1').decode('utf8', errors)


def env_to_h(v: str) -> str:
    """
    Converts an environment variable name to a hyphen-separated lowercase
    string.

    Args:
        v (str): The environment variable name.

    Returns:
        str: The converted string.
    """
    return v.replace('_', '-').lower()


def get_request() -> t.Optional[Request]:
    return getattr(ThreadSafeContext.instance(), 'request', None)
