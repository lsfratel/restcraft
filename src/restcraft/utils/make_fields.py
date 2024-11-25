from typing import Any


def make_fields(fields: dict[str, list[Any]]):
    return {key: v[0] if len(v) == 1 else v for key, v in fields.items()}
