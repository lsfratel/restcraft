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
