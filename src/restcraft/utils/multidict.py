import typing as t
from collections import defaultdict


class MultiDict:
    """
    A MultiDict is a dictionary-like object that can store multiple values for
    the same key.

    The `MultiDict` class provides the following methods:

    - `add(key: str, value: t.Any)`: Adds a value to the list of values for a
      given key.
    - `get(key: str)`: Retrieves all values for a given key as a list.
    - `get_first(key: str)`: Retrieves the first value for a given key. Useful
      if you expect a single value.
    - `remove(key: str)`: Removes the key and all its associated values from
      the dictionary.
    - `remove_value(key: str, value: t.Any)`: Removes a specific value from
      the list of values associated with a key.
    - `is_empty()`: Returns True if the dictionary is empty, False otherwise.
    - `clear()`: Clears the dictionary.
    """

    def __init__(self, data: t.Optional[t.Dict[str, t.Any]] = None):
        self._dict = defaultdict(list)

        if data:
            for key, value in data.items():
                if isinstance(value, list):
                    for v in value:
                        self.add(key, v)
                else:
                    self.add(key, value)

    def keys(self):
        """
        Returns a list of all keys in the dictionary.
        """
        return self._dict.keys()

    def add(self, key: str, value: t.Any):
        """
        Adds a value to the list of values for a given key.
        """
        self._dict[key].append(value)

    def get(self, key: str, *, default=None, index=-1, type=None):
        """
        Retrieves a value for a given key.
        """
        try:
            val = self._dict[key][index]
            return type(val) if type else val
        except IndexError:
            pass

        return default

    def get_first(self, key: str):
        """
        Retrieves the first value for a given key. Useful if you expect a
        single value.
        """
        return self._dict[key][0] if self._dict[key] else None

    def remove(self, key: str):
        """
        Removes the key and all its associated values from the dictionary.
        """
        if key in self._dict:
            del self._dict[key]

    def remove_value(self, key: str, value: t.Any):
        """
        Removes a specific value from the list of values associated with a key.
        """
        if key in self._dict:
            try:
                self._dict[key].remove(value)
                if not self._dict[key]:
                    del self._dict[key]
            except ValueError:
                pass

    def is_empty(self):
        """
        Returns True if the dictionary is empty, False otherwise.
        """
        return not bool(self._dict)

    def clear(self):
        """
        Clears the dictionary.
        """
        self._dict.clear()

    def __len__(self):
        """
        Returns the number of unique keys in the dictionary.
        """
        return len(self._dict)

    def __getitem__(self, key: str):
        """
        Allows dictionary-like get operation.
        """
        return self.get(key)

    def __setitem__(self, key: str, value: t.Any):
        """
        Allows dictionary-like set operation.

        Replaces current values with a new list containing the specified value.
        """
        self.add(key, value)

    def __delitem__(self, key: str):
        """
        Allows dictionary-like deletion of a key.
        """
        self.remove(key)

    def __contains__(self, key: str):
        """
        Check if a key is in the dictionary.
        """
        return key in self._dict

    def __iter__(self):
        """
        Returns an iterator over the dictionary's keys.
        """
        return iter(self._dict)

    def __eq__(self, other: t.Any):
        """
        Checks if another MultiDict is equal to this one based on keys and
        corresponding values.
        """
        if isinstance(other, MultiDict):
            return dict(self._dict) == dict(other._dict)
        elif isinstance(other, dict):
            return dict(self._dict) == other
        return False

    def __repr__(self) -> str:
        return f'<MultiDict {dict(self._dict)}>'
