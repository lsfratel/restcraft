import threading
import typing as t


class ThreadSafeContext:
    """
    A thread-safe context manager that allows storing and accessing values in
    a thread-local context.
    """

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


class UploadedFile:
    """
    Represents an uploaded file.

    Attributes:
        filename (str): The name of the uploaded file.
        content_type (str): The content type of the uploaded file.
        filepath (str): The file path of the uploaded file.
    """

    __slots__ = ('filename', 'content_type', 'filepath')

    def __init__(self, filename: str, content_type: str, filepath: str):
        self.filename = filename
        self.content_type = content_type
        self.filepath = filepath

    def __repr__(self) -> str:
        return f'<UploadedFile {self.filename} {self.filepath}>'


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
