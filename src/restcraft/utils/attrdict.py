class AttrDict(dict):
    """
    Dictionary subclass that allows access to keys as attributes.

    This class provides a dictionary-like object that allows access to keys
    using attribute notation instead of dictionary indexing.

    """

    __slots__ = ()

    def __getattr__(self, name):
        """
        Retrieve the value associated with the specified name.

        Args:
            name (str): The name of the attribute.

        Returns:
            The value associated with the specified name.
        """
        return self[name]

    def __setattr__(self, name, value):
        """
        Set the value associated with the specified name.

        Args:
            name (str): The name of the attribute.
            value: The value to associate with the specified name.
        """
        self[name] = value

    def __delattr__(self, name):
        """
        Remove the value associated with the specified name.

        Args:
            name (str): The name of the attribute.
        """
        del self[name]

    def __repr__(self):
        """
        Return a string representation of the dictionary.

        Returns:
            A string representation of the dictionary.
        """
        return repr(dict(self))

    def __eq__(self, other):
        """
        Return True if the dictionary is equal to the specified other object,
        False otherwise.

        Args:
            other: The object to compare against.

        Returns:
            True if the dictionary is equal to the specified other object,
            False otherwise.
        """
        return dict(self) == other

    def __ne__(self, other):
        """
        Return False if the dictionary is equal to the specified other object,
        True otherwise.

        Args:
            other: The object to compare against.

        Returns:
            False if the dictionary is equal to the specified other object,
            True otherwise.
        """
        return not (self == other)
