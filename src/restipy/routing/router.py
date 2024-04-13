import typing as t


class Route:
    """
    Represents a route in the application's routing system.

    A `Route` instance encapsulates the configuration for a single route,
    including the URL pattern, HTTP method, handler function, and optional
    before/after/exception handling functions.

    The `match` method can be used to check if a given URL path matches the
    route's URL pattern.
    """

    __slots__ = (
        'rule',
        'method',
        'handler',
        'before',
        'after',
        'on_exception',
    )

    def __init__(
        self,
        *,
        rule: t.Pattern[str],
        method: str,
        handler: t.Callable,
        before: t.Callable,
        after: t.Callable,
        on_exception: t.Callable,
    ) -> None:
        """
        Initializes a new `Route` instance with the provided parameters.

        Args:
            rule (typing.Pattern[str]): The URL pattern that this route should
                match.
            method (str): The HTTP method that this route should handle
                (e.g. "GET", "POST", etc.).
            handler (typing.Callable): The function that should be called to
                handle requests for this route.
            before (typing.Callable): A function that should be called before
                the main handler function.
            after (typing.Callable): A function that should be called after
                the main handler function.
            on_exception (typing.Callable): A function that should be called
                if an exception is raised during the request handling.
        """
        self.rule = rule
        self.method = method
        self.handler = handler
        self.before = before
        self.after = after
        self.on_exception = on_exception

    def match(self, path: str) -> t.Match[str] | None:
        """
        Matches the provided `path` against the URL pattern defined in the
        `rule` attribute of the `Route` instance.

        Args:
            path (str): The URL path to match against the route's URL pattern.

        Returns:
            typing.Match[str] | None: The match object if the path matches the
            route's URL pattern, otherwise `None`.
        """
        return self.rule.match(path)

    def __repr__(self) -> str:
        """
        Returns a string representation of the `Route` instance, including the
        HTTP method and the URL pattern.

        Returns:
            str: A string representation of the `Route` instance.
        """
        return f'<Route {self.method} {self.rule.pattern}>'
