import typing as t


class Route:
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
        self.rule = rule
        self.method = method
        self.handler = handler
        self.before = before
        self.after = after
        self.on_exception = on_exception

    def match(self, path: str) -> t.Match[str] | None:
        return self.rule.match(path)
