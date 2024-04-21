import threading
import typing as t


class ThreadSafeContext:
    """
    A thread-safe context manager that allows storing and accessing values in
    a thread-local context.
    """

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes a new instance of the ThreadSafeContext class.
        """
        object.__setattr__(self, '_ctx', threading.local())

    def clear(self) -> None:
        """
        Clears the context by removing all stored values.
        """
        if hasattr(self._ctx, 'ctx'):
            self._ctx.ctx.clear()

    def __getattr__(self, name: str) -> t.Any:
        """
        Retrieves the value associated with the specified name from the
        context.

        Args:
            name (str): The name of the value to retrieve.

        Returns:
            Any: The value associated with the specified name.

        Raises:
            AttributeError: If the specified name is not set in the context.
        """
        try:
            return self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __setattr__(self, name: str, value: t.Any) -> None:
        """
        Sets the value associated with the specified name in the context.

        Args:
            name (str): The name of the value to set.
            value (Any): The value to associate with the specified name.
        """
        if not hasattr(self._ctx, 'ctx'):
            self._ctx.ctx = {}

        self._ctx.ctx[name] = value

    def __delattr__(self, name: str) -> None:
        """
        Removes the value associated with the specified name from the context.

        Args:
            name (str): The name of the value to remove.

        Raises:
            AttributeError: If the specified name is not set in the context.
        """
        try:
            del self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __getitem__(self, name: str) -> t.Any:
        """
        Retrieves the value associated with the specified name from the
        context.

        Args:
            name (str): The name of the value to retrieve.

        Returns:
            Any: The value associated with the specified name.

        Raises:
            AttributeError: If the specified name is not set in the context.
        """
        try:
            return self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __setitem__(self, name: str, value: t.Any) -> None:
        """
        Sets the value associated with the specified name in the context.

        Args:
            name (str): The name of the value to set.
            value (Any): The value to associate with the specified name.
        """
        if not hasattr(self._ctx, 'ctx'):
            self._ctx.ctx = {}

        self._ctx.ctx[name] = value
