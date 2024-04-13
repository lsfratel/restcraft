def pep3333(value: str, errors='strict'):
    """
    Converts a string value to a UTF-8 encoded byte string, handling encoding
    errors according to the specified error handling mode.

    Args:
        value (str): The string value to be converted.
        errors (str, optional): The error handling mode, defaults to 'strict'.

    Returns:
        str: The UTF-8 encoded string.
    """
    return str(value).encode('latin1').decode('utf8', errors)


def env_to_h(v: str) -> str:
    """
    Converts an environment variable string to a hyphen-separated lowercase
    string.

    Args:
        v (str): The environment variable string to be converted.

    Returns:
        str: The converted string with hyphens and lowercase.
    """
    return v.replace('_', '-').lower()
