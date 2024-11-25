from inspect import getmembers, ismethod


def _get_funcs(cls: object, attr="__metadata__"):
    return (
        (name, func)
        for name, func in getmembers(cls, predicate=ismethod)
        if hasattr(func, attr)
    )


def extract_metadata(cls: object):
    for _, func in _get_funcs(cls):
        func_metadata = getattr(func, "__metadata__", {})

        http_verbs = func_metadata.get("methods", None)

        if not http_verbs:
            continue

        for verb in http_verbs:
            yield verb, func, func_metadata
