import importlib
import os
import typing as t
from types import ModuleType

from restcraft.core.exceptions import RestCraftException


class LazySettings:
    """
    Provides a lazy settings class that loads settings from a module specified
    by the `RESTCRAFT_SETTINGS_MODULE` environment variable.
    """

    settings_module = os.environ.get('RESTCRAFT_SETTINGS_MODULE', '')

    def __init__(self) -> None:
        self._module: ModuleType
        self._setup()

    def _setup(self) -> None:
        try:
            self._module = importlib.import_module(self.settings_module)
        except ImportError as e:
            raise RestCraftException(
                f'Could not import settings module "{self.settings_module}".'
            ) from e

    def __getattr__(self, name: str) -> t.Any:
        if not hasattr(self._module, name):
            raise AttributeError('')
        return getattr(self._module, name)


settings = LazySettings()
