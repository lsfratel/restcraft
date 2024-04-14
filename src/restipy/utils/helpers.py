import threading
import typing as t


class ThreadSafeContext:
    """
    A context manager that provides a thread-local storage for storing and
    retrieving arbitrary data.

    The `ContextManager` class provides a simple way to store and retrieve
    data in a thread-local context. This can be useful for passing data
    between functions or components without having to pass it explicitly
    as arguments.

    The context is stored in a dictionary-like object, where keys are used
    to access the stored values. The context is scoped to the current thread,
    so each thread has its own independent context.
    """

    def __init__(self) -> None:
        """
        Sets the `_ctx` attribute of the `ContextManager` instance to a new
        `threading.local()` object. This creates a thread-local storage for
        storing and retrieving data in the context manager.
        """
        object.__setattr__(self, '_ctx', threading.local())

    def clear(self) -> None:
        """
        Clears the thread-local context dictionary.
        """
        if hasattr(self._ctx, 'ctx'):
            self._ctx.ctx.clear()

    def __getattr__(self, name: str) -> t.Any:
        """
        Retrieves a value from the thread-local context dictionary. If the
        requested key is not found in the context, an `AttributeError` is
        raised with a descriptive error message.

        Args:
            `name (str):` The key to retrieve from the thread-local context
                dictionary.

        Returns:
            Any: The value associated with the requested key in the
            thread-local context.

        Raises:
            AttributeError: If the requested key is not found in the
            thread-local context.
        """
        try:
            return self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __setattr__(self, name: str, value: t.Any) -> None:
        """
        Sets a value in the thread-local context dictionary.

        Args:
            `name (str):` The key to set in the thread-local context
                dictionary.
            `value (Any):` The value to associate with the key in the
                thread-local context.

        Raises:
            `AttributeError:` If the `name` argument is not a valid attribute
                name.
        """
        if not hasattr(self._ctx, 'ctx'):
            self._ctx.ctx = {}

        self._ctx.ctx[name] = value

    def __delattr__(self, name: str) -> None:
        """
        Removes a value from the thread-local context dictionary. If the
        requested key is not found in the context, an `AttributeError` is
        raised with a descriptive error message.

        Args:
            `name (str):` The key to remove from the thread-local context
                dictionary.

        Raises:
            `AttributeError:` If the requested key is not found in the
                thread-local context.
        """
        try:
            del self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __getitem__(self, name: str) -> t.Any:
        """
        Retrieves a value from the thread-local context dictionary.

        Args:
            `name (str):` The key to retrieve from the thread-local context
                dictionary.

        Returns:
            `Any:` The value associated with the requested key in the
                thread-local context.

        Raises:
            `AttributeError:` If the requested key is not found in the
                thread-local context.
        """
        try:
            return self._ctx.ctx[name]
        except KeyError as e:
            raise AttributeError(f'{name} is not set in the context') from e

    def __setitem__(self, name: str, value: t.Any) -> None:
        """
        Sets a value in the thread-local context dictionary.

        Args:
            `name (str):` The key to set in the thread-local context
                dictionary.
            `value (Any):` The value to associate with the key in the
                thread-local context.

        Raises:
            `AttributeError:` If the `name` argument is not a valid attribute
                name.
        """
        if not hasattr(self._ctx, 'ctx'):
            self._ctx.ctx = {}

        self._ctx.ctx[name] = value


class UploadedFile:
    """
    Represents an uploaded file, containing the filename, content type,
    and file path.

    Args:
        `filename (str):` The name of the uploaded file.
        `content_type (str):` The MIME type of the uploaded file.
        `filepath (str):` The file path of the uploaded file.

    Attributes:
        `filename (str):` The name of the uploaded file.
        `content_type (str):` The MIME type of the uploaded file.
        `filepath (str):` The file path of the uploaded file.
    """

    __slots__ = ('filename', 'content_type', 'filepath')

    def __init__(self, filename: str, content_type: str, filepath: str):
        self.filename = filename
        self.content_type = content_type
        self.filepath = filepath

    def __repr__(self) -> str:
        return f'<UploadedFile {self.filename} {self.filepath}>'


def pep3333(value: str, errors='strict'):
    """
    Converts a string value to a UTF-8 encoded byte string, handling encoding
    errors according to the specified error handling mode.

    Args:
        `value (str):` The string value to be converted.
        `errors (str, optional):` The error handling mode, defaults to
            'strict'.

    Returns:
        `str:` The UTF-8 encoded string.
    """
    return str(value).encode('latin1').decode('utf8', errors)


def env_to_h(v: str) -> str:
    """
    Converts an environment variable string to a hyphen-separated lowercase
    string.

    Args:
        `v (str):` The environment variable string to be converted.

    Returns:
        `str:` The converted string with hyphens and lowercase.
    """
    return v.replace('_', '-').lower()
