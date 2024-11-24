from __future__ import annotations

from collections.abc import Callable
from typing import Any


def metadata(
    *,
    methods: list[str],
    plugins: list[str] = ["..."],
    **options,
):
    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        metadata = {
            "methods": methods,
            "plugins": plugins,
            **options,
        }
        setattr(func, "__metadata__", metadata)
        return func

    return inner
