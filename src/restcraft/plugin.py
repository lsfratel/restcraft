from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from restcraft.http import Response
    from restcraft.restcraft import RestCraft


class PluginException(Exception):
    pass


class Plugin:
    name: str

    def setup(self, app: RestCraft):
        pass

    def apply(
        self, callback: Callable[..., Response], metadata: dict[str, Any]
    ) -> Callable[..., Response]:
        return callback

    def close(self):
        pass
