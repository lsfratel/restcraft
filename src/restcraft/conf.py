import importlib
import os
import typing as t
from types import ModuleType


class LazySettings:
    """
    A class that provides lazy access to settings module attributes.

    The LazySettings class allows accessing attributes from the settings module
    in a lazy manner. It imports the settings module only when an attribute is
    accessed, and raises an exception if the attribute is not set.

    Attributes:
        settings_module (str): The name/path of the settings module.

    Methods:
        __init__: Initializes the LazySettings instance.
        _setup: Imports the settings module.
        __getattr__: Retrieves the value of an attribute from the settings
            module.

    """

    settings_module = os.environ.get('RESTCRAFT_SETTINGS_MODULE', '')

    def __init__(self) -> None:
        """
        Initializes the LazySettings instance.
        """
        self._module: ModuleType
        self._setup()

    def _setup(self) -> None:
        """
        Imports the settings module.
        """
        try:
            self._module = importlib.import_module(self.settings_module)
        except ImportError:
            raise

    def __getattr__(self, name: str) -> t.Any:
        """
        Retrieves the value of an attribute from the settings module.

        Args:
            name (str): The name of the attribute.

        Returns:
            Any: The value of the attribute.

        Raises:
            ValueError: If the attribute is not set in the settings
                module.
        """
        if not hasattr(self._module, name):
            raise ValueError(f'{name} not set in settings module.')
        return getattr(self._module, name)


settings = LazySettings()
