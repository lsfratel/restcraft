import json
import typing as t
from http import client as httplib

from restipy.core.exceptions import RestiPyException
from restipy.utils.helpers import pep3333

_HTTP_CODES = httplib.responses.copy()
_HTTP_CODES[418] = "I'm a teapot"
_HTTP_CODES[428] = 'Precondition Required'
_HTTP_CODES[429] = 'Too Many Requests'
_HTTP_CODES[431] = 'Request Header Fields Too Large'
_HTTP_CODES[451] = 'Unavailable For Legal Reasons'
_HTTP_CODES[511] = 'Network Authentication Required'
_HTTP_STATUS_LINES = {k: '%d %s' % (k, v) for (k, v) in _HTTP_CODES.items()}


class BaseResponse:
    """
    Represents a base response object for a RESTful API.

    The `BaseResponse` class provides a set of properties and methods to manage
    the response data, status code, and headers for a RESTful API. It includes
    functionality to handle common HTTP response headers and status codes, as
    well as methods to get the encoded response data, status line, and headers.

    The class has the following attributes:
    - `_body`: The response body data.
    - `_status`: The HTTP status code for the response.
    - `_headers`: The HTTP headers for the response.
    - `_encoded_data`: The encoded version of the response body data.

    The class also has the following methods:
    - `header_list`: Returns a list of headers in the response, with certain
      headers removed based on the response status code.
    - `header`: Returns the headers of the response.
    - `status`: Returns the status of the response.
    - `status_line`: Returns the status line corresponding to the current
      status code.
    - `set_status`: Sets the status code for the response.
    - `data`: Returns the body of the response.
    - `set_data`: Sets the data for the response body.
    - `_get_encoded_data`: Returns the encoded version of the response body.
    - `get_response`: Returns the response data, status line, and headers as a
      tuple.
    """

    __slots__ = ('_body', '_status', '_headers', '_encoded_data')

    default_headers = {'content-type': 'text/plain; charset=utf-8'}
    bad_headers = {
        204: ('Content-Type', 'Content-Length'),
        304: (
            'Allow',
            'Content-Encoding',
            'Content-Language',
            'Content-Length',
            'Content-Range',
            'Content-Type',
            'Content-Md5',
            'Last-Modified',
        ),
    }

    def __init__(
        self, body: t.Any, *, status_code=200, headers: dict[str, t.Any] = {}
    ) -> None:
        """
        Initializes a new instance of the `Response` class with the given body,
        status code, and headers.

        Args:
            `body (Any):` The response body data.
            `status_code (int, optional):` The HTTP status code for the
                response. Defaults to 200.
            `headers (dict[str, Any], optional):` The HTTP headers for the
                response. Defaults to an empty dictionary.

        Attributes:
            `_body (Any):` The response body data.
            `_status (int):` The HTTP status code for the response.
            `_headers (dict[str, Any]):` The HTTP headers for the response.
            `_encoded_data (bytes):` The encoded version of the response body
                data.
            `encode (callable):` A reference to the `json.dumps` function.
        """
        self._body = body
        self._status = status_code
        self._headers = self.default_headers.copy()
        for k, v in headers.items():
            self._headers[k.lower()] = v

    @property
    def header_list(self):
        """
        Returns a list of headers in the response.

        If the response status is in the `bad_headers` dictionary,
        it removes any headers specified in the dictionary from the response
        headers. Then, it converts the remaining headers into a list of tuples,
        where each tuple contains the header name and its corresponding value.

        Returns:
            `list[tuple[str, str]]:` A list of tuples representing the headers
                in the response.
        """
        if self._status in self.bad_headers:
            bad_headers = self.bad_headers[self._status]
            for header in bad_headers:
                if header.lower() in self._headers:
                    del self._headers[header.lower()]
        return [(k, pep3333(v)) for k, v in self._headers.items()]

    @property
    def header(self):
        """
        Returns the headers of the response.

        Returns:
            `dict[str, str]:` The headers of the response.
        """
        return self._headers

    @property
    def status(self):
        """
        Returns the status of the response.

        Returns:
            `int:` The status of the response.
        """
        return self._status

    @property
    def status_line(self):
        """
        Returns the status line corresponding to the current status code.

        Returns:
            `str:` The status line corresponding to the current status code.
        """
        return _HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int):
        """
        Sets the status of the response.

        Args:
            `status (int):` The status code to set for the response.

        Raises:
            `RestiPyException:` If the provided `status` is not a valid HTTP
                status code.
        """
        if status not in _HTTP_CODES:
            raise RestiPyException('Invalid status code.')
        self._status = status

    @property
    def data(self):
        """
        Returns the body of the response.

        Returns:
            `Any:` The body of the response.
        """
        return self._body

    @data.setter
    def set_data(self, data: t.Any):
        """
        Set the data for the response body.

        Args:
            `data (Any):` The data to be set as the response body.
        """
        self._body = data
        self._encoded_data = None

    def _encode(self):
        return str(self._body).encode()

    def _get_encoded_data(self):
        """
        Returns the encoded version of the response body.

        Returns:
            `bytes:` The encoded version of the response body.
        """
        return self._encode()

    def get_response(self):
        """
        Returns the encoded response data, status line, and headers.

        Returns:
            `tuple[bytes, str, list[str]]:` The encoded response data, status
                line, and headers.
        """
        data = self._get_encoded_data()
        self.header['content-length'] = str(len(data))
        status = self.status_line
        headers = self.header_list
        return (data, status, headers)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Response object.

        The string representation includes the class name and the status line.

        Returns:
            `str:` The string representation of the Response object.
        """
        return f'<{self.__class__.__name__} {self.status_line}>'


class Response(BaseResponse):
    default_headers = {'content-type': 'application/json; charset=utf-8'}

    def _encode(self):
        return json.dumps(self._body).encode()
