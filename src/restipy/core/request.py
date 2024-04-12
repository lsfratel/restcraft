from __future__ import annotations

import json
import typing as t
from urllib.parse import parse_qs, urljoin

from restipy.core.exceptions import (
    MalformedBodyException,
    RequestBodyTooLargeException,
)
from restipy.utils.helpers import env_to_h

if t.TYPE_CHECKING:
    from restipy.core.application import RestiPy


class Request:
    __slots__ = ('_params', '_body', '_headers', 'env', 'ctx')

    def __init__(self, environ: dict, params: dict = {}) -> None:
        self.env = environ
        self._params = params
        self._body: t.Any = None
        self._headers: t.Any = None
        self.ctx: dict[str, t.Any] = {}

    def _read_body(self) -> None | bytes:
        if self.method not in ('POST', 'PUT', 'PATCH'):
            return None
        max_body_size = self.app.config.MAX_BODY_SIZE
        if self.content_length > max_body_size:
            raise RequestBodyTooLargeException('Request body too large.')
        max_read = max(self.content_length, max_body_size)
        body = self.env['wsgi.input'].read(max_read + 1)
        if len(body) > max_read:
            raise RequestBodyTooLargeException('Request body too large.')
        return body

    @property
    def app(self) -> RestiPy:
        return self.env['restipy.app']

    @property
    def params(self) -> dict[str, t.Any]:
        return self._params

    @params.setter
    def set_params(self, params: dict):
        self._params = params

    @property
    def json(self) -> dict[str, t.Any] | None:
        ctype = self.content_type.lower().split(';')[0]
        if ctype not in ('application/json', 'application/json-rpc'):
            return None
        b = self._read_body()
        if not b:
            return None
        try:
            self._body = json.loads(b)
        except Exception as e:
            raise MalformedBodyException(
                'Malformed JSON body.', status_code=400
            ) from e
        return self._body

    @property
    def form(self) -> dict[str, list[t.Any]] | None:
        if self.content_type.startswith('multipart/'):
            return None
        b = self._read_body()
        if b is None:
            return None
        try:
            self._body = parse_qs(b.decode())
        except Exception as e:
            raise MalformedBodyException(
                'Malformed form body.', status_code=400
            ) from e
        return self._body

    @property
    def header(self) -> dict[str, str]:
        if self._headers is None:
            self._headers = {
                env_to_h(k)[5:]: v
                for k, v in self.env.items()
                if k.startswith('HTTP_')
            }
        return self._headers

    @property
    def origin(self) -> str:
        return f'{self.protocol}://{self.host}'.lower()

    @property
    def url(self) -> str:
        return urljoin(self.origin, self.path).rstrip('/')

    @property
    def href(self) -> str:
        return f'{self.url}?{self.env.get("QUERY_STRING", "")}'

    @property
    def method(self) -> str:
        return self.env.get('REQUEST_METHOD', 'GET').upper()

    @property
    def path(self) -> str:
        return self.env.get('PATH_INFO', '/')

    @property
    def query(self) -> dict[str, list[t.Any]] | None:
        qs = self.env.get('QUERY_STRING')
        if qs is None:
            return qs
        return parse_qs(qs)

    @property
    def host(self) -> None:
        return self.env.get('HTTP_HOST')

    @property
    def charset(self) -> str | None:
        if self.content_type is None:
            return None
        for part in self.content_type.split(';'):
            if 'charset=' in part:
                return part.split('=')[1].strip()
        return None

    @property
    def content_length(self) -> int:
        return int(self.env.get('CONTENT_LENGTH', '0'))

    @property
    def protocol(self) -> str:
        return self.env.get('wsgi.url_scheme', 'http').upper()

    @property
    def secure(self) -> bool:
        return self.protocol == 'HTTPS'

    @property
    def accept(self) -> str | None:
        accept = self.env.get('HTTP_ACCEPT')
        if accept:
            return accept.lower()
        return accept

    @property
    def content_type(self) -> str:
        return self.env.get('CONTENT_TYPE', '')
