from __future__ import annotations

import json
import typing as t
from urllib.parse import parse_qs, urljoin

from restipy.core.exceptions import MalformedBodyException
from restipy.utils.helpers import env_to_h

if t.TYPE_CHECKING:
    from restipy.core.application import RestiPy


class Request:
    __slots__ = ('env', '_params', '_body', '_headers')

    def __init__(self, environ: dict, params: dict = {}) -> None:
        self.env = environ
        self._params = params
        self._body: t.Any = None
        self._headers: t.Any = None

    def _read_body(self) -> None | bytes:
        read = self.env['wsgi.input'].read
        body = read(1)
        if not body:
            return None
        while True:
            c = read(24)
            if not c:
                break
            body += c
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
        if self._body is None:
            body = self._read_body()
            if body is None:
                return body
            try:
                body = json.loads(body)
                self._body = body
            except json.JSONDecodeError as e:
                raise MalformedBodyException(
                    'Malformed JSON body.', status_code=400
                ) from e
            except Exception:
                raise
        return self._body

    @json.setter
    def set_json(self, body: dict[str, t.Any]):
        self._body = body

    @property
    def form(self) -> dict[str, list[t.Any]] | None:
        body = self._read_body()
        if body is None:
            return body
        return parse_qs(body.decode())

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
    def length(self) -> int | None:
        length = self.env.get('CONTENT_LENGTH')
        if length:
            return int(length)
        return length

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
    def content_type(self) -> str | None:
        return self.env.get('CONTENT_TYPE')
