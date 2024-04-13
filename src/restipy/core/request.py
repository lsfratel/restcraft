from __future__ import annotations

import json
import typing as t
from urllib.parse import parse_qs, urljoin

from restipy.core.exceptions import HTTPException
from restipy.utils.helpers import env_to_h

if t.TYPE_CHECKING:
    from restipy.core.application import RestiPy


class Request:
    """
    Represents a request to the RestiPy application.

    The `Request` class encapsulates the details of an incoming HTTP request,
    providing access to the request parameters, headers, body, and other
    relevant information. It is used internally by the RestiPy application to
    handle and process incoming requests.

    The `Request` class provides properties and methods to access various
    aspects of the request, such as the HTTP method, path, query parameters,
    headers, and request body. It also handles parsing of the request body,
    including JSON and form data.

    This class is not intended to be used directly by application developers,
    but rather is used internally by the RestiPy framework to handle incoming
    requests.
    """

    __slots__ = ('_params', '_body', '_headers', 'env', 'ctx')

    def __init__(self, environ: dict, params: dict = {}) -> None:
        """
        Initializes a new instance of the Request class.

        Args:
            `environ (dict):` The WSGI environment dictionary.
            `params (dict, optional):` The request parameters. Defaults to an
                empty dictionary.
        """
        self.env = environ
        self._params = params
        self._body: t.Any = None
        self._headers: t.Any = None
        self.ctx: dict[str, t.Any] = {}

    def _read_body(self) -> None | bytes:
        """
        Reads and returns the request body.

        Returns:
            `bytes or None:` The request body, or None if the request method is
                not 'POST', 'PUT', or 'PATCH'.
        """
        if self.method not in ('POST', 'PUT', 'PATCH'):
            return None
        max_body_size = self.app.config.MAX_BODY_SIZE
        if self.content_length > max_body_size:
            raise HTTPException(
                'Request body too large.',
                status_code=413,
                code='REQUEST_BODY_TOO_LARGE',
            )
        max_read = max(self.content_length, max_body_size)
        body = self.env['wsgi.input'].read(max_read + 1)
        if len(body) > max_read:
            raise HTTPException(
                'Request body too large.',
                status_code=413,
                code='REQUEST_BODY_TOO_LARGE',
            )
        return body

    @property
    def app(self) -> RestiPy:
        """
        The RestiPy application instance.

        Returns:
            `RestiPy:` The RestiPy application instance.
        """
        return self.env['restipy.app']

    @property
    def params(self) -> dict[str, t.Any]:
        """
        The request parameters.

        Returns:
            `dict:` The request parameters.
        """
        return self._params

    @params.setter
    def set_params(self, params: dict):
        """
        Set the parameters for the request.

        Args:
            `params (dict):` A dictionary containing the parameters to be set.
        """
        self._params = params

    @property
    def json(self) -> dict[str, t.Any] | None:
        """
        The JSON body of the request, if the content type is
        'application/json'.

        Returns:
            `dict or None:` The JSON body of the request, or None if the
                content type is not 'application/json'.
        """
        ctype = self.content_type.lower().split(';')[0]
        if ctype not in ('application/json', 'application/json-rpc'):
            return None
        b = self._read_body()
        if not b:
            return None
        try:
            self._body = json.loads(b)
        except Exception as e:
            raise HTTPException(
                'Malformed JSON body.', status_code=400, code='MALFORMED_JSON'
            ) from e
        return self._body

    @property
    def form(self) -> dict[str, list[t.Any]] | None:
        """
        The form data of the request, if the content type is not 'multipart/'.

        Returns:
            `dict or None:` The form data of the request, or None if the
                content type is 'multipart/'.
        """
        if self.content_type.startswith('multipart/'):
            return None
        b = self._read_body()
        if b is None:
            return None
        try:
            self._body = parse_qs(b.decode())
        except Exception as e:
            raise HTTPException(
                'Malformed JSON body.', status_code=400, code='MALFORMED_JSON'
            ) from e
        return self._body

    @property
    def header(self) -> dict[str, str]:
        """
        The request headers.

        Returns:
            `dict:` The request headers.
        """
        if self._headers is None:
            self._headers = {
                env_to_h(k)[5:]: v
                for k, v in self.env.items()
                if k.startswith('HTTP_')
            }
        return self._headers

    @property
    def origin(self) -> str:
        """
        The origin of the request.

        Returns:
            `str:` The origin of the request.
        """
        return f'{self.protocol}://{self.host}'.lower()

    @property
    def url(self) -> str:
        """
        The full URL of the request.

        Returns:
            `str:` The full URL of the request.
        """
        return urljoin(self.origin, self.path).rstrip('/')

    @property
    def href(self) -> str:
        """
        The href of the request.

        Returns:
            `str:` The href of the request.
        """
        return f'{self.url}?{self.env.get("QUERY_STRING", "")}'

    @property
    def method(self) -> str:
        """
        The HTTP method of the request.

        Returns:
            `str:` The HTTP method of the request.
        """
        return self.env.get('REQUEST_METHOD', 'GET').upper()

    @property
    def path(self) -> str:
        """
        The path of the request.

        Returns:
            `str:` The path of the request.
        """
        return self.env.get('PATH_INFO', '/')

    @property
    def query(self) -> dict[str, list[t.Any]] | None:
        """
        The query parameters of the request.

        Returns:
            `dict or None:` The query parameters of the request, or None if
                there are no query parameters.
        """
        qs = self.env.get('QUERY_STRING')
        if qs is None:
            return qs
        return parse_qs(qs)

    @property
    def host(self) -> None:
        """
        The host of the request.

        Returns:
            `str or None:` The host of the request.
        """
        return self.env.get('HTTP_HOST')

    @property
    def charset(self) -> str | None:
        """
        The charset of the request.

        Returns:
            `str or None:` The charset of the request.
        """
        if self.content_type is None:
            return None
        for part in self.content_type.split(';'):
            if 'charset=' in part:
                return part.split('=')[1].strip()
        return None

    @property
    def content_length(self) -> int:
        """
        The content length of the request.

        Returns:
            `int:` The content length of the request.
        """
        return int(self.env.get('CONTENT_LENGTH', '0'))

    @property
    def protocol(self) -> str:
        """
        The protocol of the request.

        Returns:
            `str:` The protocol of the request.
        """
        return self.env.get('wsgi.url_scheme', 'http').upper()

    @property
    def secure(self) -> bool:
        """
        Whether the request is secure (HTTPS).

        Returns:
            `bool:` True if the request is secure, False otherwise.
        """
        return self.protocol == 'HTTPS'

    @property
    def accept(self) -> str | None:
        """
        The accept header of the request.

        Returns:
            `str or None:` The accept header of the request.
        """
        accept = self.env.get('HTTP_ACCEPT')
        if accept:
            return accept.lower()
        return accept

    @property
    def content_type(self) -> str:
        """
        The content type of the request.

        Returns:
            `str:` The content type of the request.
        """
        return self.env.get('CONTENT_TYPE', '')

    def __repr__(self) -> str:
        """
        Returns a string representation of the Request object.

        Returns:
            `str:` A string representation of the Request object.
        """
        return f'<Request {self.method} {self.path}>'
