from collections.abc import Generator
from copy import deepcopy
from inspect import getmembers, ismethod
from types import MethodType
from typing import Any


def _get_metadata_methods(cls: object, attr="__metadata__"):
    return (
        method
        for _, method in getmembers(cls, predicate=ismethod)
        if hasattr(method, attr)
    )


def extract_metadata(
    cls: object,
) -> Generator[tuple[dict[str, Any], MethodType], None, None]:
    for method in _get_metadata_methods(cls):
        metadata = getattr(method, "__metadata__")

        yield deepcopy(metadata), method
