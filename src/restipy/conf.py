import importlib
import os
import typing as t
from types import ModuleType

from restipy.core.exceptions import RestiPyException


class LazySettings:
    """
    Provides a lazy settings class that loads settings from a module specified
    by the `RESTIPY_SETTINGS_MODULE` environment variable.
    """

    settings_module = os.environ.get('RESTIPY_SETTINGS_MODULE', '')

    def __init__(self) -> None:
        self._module: ModuleType
        self._setup()

    def _setup(self):
        try:
            self._module = importlib.import_module(self.settings_module)
        except ImportError as e:
            raise RestiPyException(
                f'Could not import settings module "{self.settings_module}".'
            ) from e

    def __getattr__(self, name: str) -> t.Any:
        if not hasattr(self._module, name):
            raise AttributeError('')
        return getattr(self._module, name)


settings = LazySettings()
