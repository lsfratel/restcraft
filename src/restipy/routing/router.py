import typing as t


class Route:
    def __init__(
        self, rule: t.Pattern[str], method: str, handler: t.Callable
    ) -> None:
        self.rule = rule
        self.method = method
        self.handler = handler

    def match(self, path: str) -> t.Match[str] | None:
        return self.rule.match(path)
