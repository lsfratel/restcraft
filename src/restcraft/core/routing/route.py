from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from .types import ParamType
    from .view import View


class Route:
    """
    The `Route` class represents a route in the application.

    It encapsulates the view function, parameter types, and the regular
    expression pattern used to match the URL. The class provides methods to
    validate the route pattern, parse the pattern into a regular expression
    and parameter names, and match a given URL against the route.
    """

    __slots__ = ('view', 'regex', 'params')

    def __init__(
        self,
        view: View,
        regex: t.Pattern[str],
        params: t.List[t.Tuple[str, t.Type[ParamType], bool]],
    ):
        self.view = view
        self.regex = regex
        self.params = params

    def match(self, url: str) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Attempts to match the provided URL against the route's regular
        expression pattern, and if successful, returns a dictionary of the
        extracted parameter values.

        Args:
            url (str): The URL to match against the route's pattern.

        Returns:
            Optional[Dict[str, Any]]: If the URL matches the route's pattern,
                a dictionary containing the extracted parameter values is
                returned. Otherwise, `None` is returned.
        """
        match = self.regex.match(url)

        if not match:
            return None

        params: t.Dict[str, t.Any] = {}

        for (name, type_, _), value in zip(
            self.params, match.groups(), strict=False
        ):
            params[name] = type_.convert(value) if value else None

        return params
