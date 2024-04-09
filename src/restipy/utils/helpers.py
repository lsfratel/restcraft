def pep3333(value: str, errors='strict'):
    return str(value).encode('latin1').decode('utf8', errors)


def re_route(method: str, rule: str, handler: str) -> tuple[str, str, str]:
    return (method, rule, handler)


def env_to_h(v: str) -> str:
    return v.replace('_', '-').lower()
