from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


def metadata(
    *,
    methods: list[str],
    plugins: list[str] = ["..."],
    **options,
):
    """Decorator for adding metadata to a view function.

    Args:
        methods (list[str]): A list of HTTP methods supported by the view.
        plugins (list[str], optional): A list of plugins to include or exclude.
            Defaults to ["..."].
        **options: Additional metadata to be added to the view function.

    Returns:
        Callable[..., Any]: The wrapped view function.
    """

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        metadata = {
            "methods": methods,
            "plugins": plugins,
            **options,
        }
        setattr(func, "__metadata__", metadata)
        return func

    return inner
