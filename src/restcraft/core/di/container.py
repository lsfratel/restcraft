from __future__ import annotations

import inspect
import threading
import typing as t
from functools import wraps


class DependencyManager:
    """
    DependencyManager is a singleton that manages dependencies for the
    application.

    It holds a dictionary of dependencies, their corresponding scope and
    provides methods to register, resolve and clear scoped dependencies.
    """

    _instance = None

    @classmethod
    def instance(cls) -> DependencyManager:
        """
        Returns the instance of DependencyManager. If it doesn't exist, it
        creates a new instance.
        """

        if cls._instance is None:
            cls._instance = DependencyManager()
        return cls._instance

    def __init__(self):
        """
        Initialize the DependencyManager with empty dictionaries for
        dependencies, singleton cache and scopes.
        """

        self._dependencies = {}
        self._singleton_cache = {}
        self._scopes = {}
        self._thread_scopes = threading.local()

    def register(self, dependency: type, scope: str = 'singleton') -> None:
        """
        Register a dependency with its corresponding scope.

        Args:
            dependency (ModuleType): The dependency to be registered.
            scope (str): The scope of the dependency. Default is 'singleton'.

        Raises:
            ValueError: If the scope is not valid.
        """

        valid_scopes = ['singleton', 'transient', 'scoped']
        if scope not in valid_scopes:
            raise ValueError(f'Invalid scope for: {dependency.__name__}')

        self._dependencies[dependency.__name__] = dependency
        self._scopes[dependency.__name__] = scope

    def resolve(self, type_: str) -> t.Any:
        """
        Resolve a dependency based on its type.

        Args:
            type_ (str): The type of the dependency.

        Returns:
            The resolved dependency.
        """

        scope = self._scopes.get(type_)

        if scope is None:
            return

        if scope == 'singleton':
            return self._get_singleton(type_)
        elif scope == 'transient':
            return self._get_transient(type_)
        else:
            return self._get_scoped(type_)

    def clear_scoped(self) -> None:
        """
        Clears the scoped dependencies for the current thread.
        """

        if hasattr(self._thread_scopes, 'scoped_dependencies'):
            self._thread_scopes.scoped_dependencies.clear()

    def _get_singleton(self, type_: str) -> t.Any:
        """
        Returns the singleton instance of a dependency. If it doesn't exist,
        it creates a new instance and caches it.

        Args:
            type_ (str): The type of the dependency.

        Returns:
            The singleton instance of the dependency.
        """

        if type_ not in self._singleton_cache:
            self._singleton_cache[type_] = self._dependencies[type_]()
        return self._singleton_cache[type_]

    def _get_transient(self, type_: str) -> t.Any:
        """
        Returns a new instance of a dependency.

        Args:
            type_ (str): The type of the dependency.

        Returns:
            The new instance of the dependency.
        """

        return self._dependencies[type_]()

    def _get_scoped(self, type_: str) -> t.Any:
        """
        Returns the scoped instance of a dependency. If it doesn't exist, it
        creates a new instance.

        Args:
            type_ (str): The type of the dependency.

        Returns:
            The scoped instance of the dependency.
        """

        if not hasattr(self._thread_scopes, 'scoped_dependencies'):
            self._thread_scopes.scoped_dependencies = {}

        if type_ not in self._thread_scopes.scoped_dependencies:
            self._thread_scopes.scoped_dependencies[type_] = (
                self._dependencies[type_]()
            )
        return self._thread_scopes.scoped_dependencies[type_]


def inject(func: t.Callable) -> t.Callable:
    """
    A decorator that injects dependencies into a function.

    This decorator inspects the function's parameters and retrieves
    dependencies from the DependencyManager. The dependencies are then
    added as keyword arguments to the function call.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.
    """
    container = DependencyManager.instance()

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        The wrapper function that injects dependencies and calls the
        decorated function.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The result of the decorated function.
        """
        signature = inspect.signature(func)

        for param_name, param in signature.parameters.items():
            annotation = param.annotation

            if hasattr(annotation, '__name__'):
                param_type = annotation.__name__
            else:
                param_type = annotation

            if param_type == inspect.Parameter.empty:
                continue

            if service := container.resolve(param_type):
                kwargs[param_name] = service

        return func(*args, **kwargs)

    return wrapper
