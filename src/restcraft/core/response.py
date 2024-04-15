import json
import os
import typing as t
from http import client as httplib
from urllib.parse import quote

from restcraft.core.exceptions import (
    FileNotFound,
    InvalidStatusCode,
    UnsupportedBodyType,
)
from restcraft.utils.helpers import pep3333

_HTTP_CODES = httplib.responses.copy()
_HTTP_CODES[418] = "I'm a teapot"
_HTTP_CODES[428] = 'Precondition Required'
_HTTP_CODES[429] = 'Too Many Requests'
_HTTP_CODES[431] = 'Request Header Fields Too Large'
_HTTP_CODES[451] = 'Unavailable For Legal Reasons'
_HTTP_CODES[511] = 'Network Authentication Required'
_HTTP_STATUS_LINES = {k: '%d %s' % (k, v) for (k, v) in _HTTP_CODES.items()}


__all__ = (
    'Response',
    'JSONResponse',
    'RedirectResponse',
    'FileResponse',
)


class Response:
    """
    Represents a base response object for a RESTful API.

    The `Response` class provides a set of properties and methods to manage
    the response data, status code, and headers for a RESTful API. It includes
    functionality to handle common HTTP response headers and status codes, as
    well as methods to get the encoded response data, status line, and headers.

    The class has the following attributes:
    - `_body`: The response body data.
    - `_status`: The HTTP status code for the response.
    - `_headers`: The HTTP headers for the response.

    The class also has the following methods:
    - `header_list`: Returns a list of headers in the response, with certain
      headers removed based on the response status code.
    - `header`: Returns the headers of the response.
    - `status`: Returns the status of the response.
    - `status_line`: Returns the status line corresponding to the current
      status code.
    - `set_status`: Sets the status code for the response.
    - `body`: Returns the body of the response.
    - `set_body`: Sets the data for the response body.
    - `_get_encoded_data`: Returns the encoded version of the response body.
    - `get_response`: Returns the response data, status line, and headers as a
      tuple.
    """

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
        self,
        body: t.Any = None,
        *,
        status_code=200,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
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
        """
        self._body = body
        self._status = status_code
        self._headers = self.default_headers.copy()
        if headers:
            for k, v in headers.items():
                self._headers[k.lower()] = v

    @property
    def header_list(self) -> t.List[t.Tuple[str, str]]:
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
    def header(self) -> t.Dict[str, str]:
        """
        Returns the headers of the response.

        Returns:
            `dict[str, str]:` The headers of the response.
        """
        return self._headers

    @property
    def status(self) -> int:
        """
        Returns the status of the response.

        Returns:
            `int:` The status of the response.
        """
        return self._status

    @property
    def status_line(self) -> str:
        """
        Returns the status line corresponding to the current status code.

        Returns:
            `str:` The status line corresponding to the current status code.
        """
        return _HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int) -> None:
        """
        Sets the status of the response.

        Args:
            `status (int):` The status code to set for the response.

        Raises:
            `RestCraftException:` If the provided `status` is not a valid HTTP
                status code.
        """
        if status not in _HTTP_CODES:
            raise InvalidStatusCode()
        self._status = status

    @property
    def body(self) -> t.Any:
        """
        Returns the body of the response.

        Returns:
            `Any:` The body of the response.
        """
        return self._body

    @body.setter
    def set_body(self, body: t.Any) -> None:
        """
        Set the data for the response body.

        Args:
            `data (Any):` The data to be set as the response body.
        """
        self._body = body

    def _encode(self) -> bytes:
        """
        Encodes the response body as a byte string.

        Returns:
            bytes: The encoded response body.
        """
        if self._body is None or self._body == '':
            return b''

        return str(self._body).encode()

    def _get_encoded_data(self) -> bytes:
        """
        Returns the encoded version of the response body.

        Returns:
            `bytes:` The encoded version of the response body.
        """
        return self._encode()

    def get_response(self) -> t.Tuple[bytes, str, t.List[t.Tuple[str, str]]]:
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


class JSONResponse(Response):
    default_headers = {'content-type': 'application/json; charset=utf-8'}

    __slots__ = ('_body', '_status', '_headers', '_encoded_data')

    def _encode(self) -> bytes:
        if self._body is None or self._body == '':
            return b''

        return json.dumps(self._body).encode()


class RedirectResponse(Response):
    """
    Represents a redirect response, which is used to redirect the client to a
    different URL.

    The `RedirectResponse` class is a subclass of the `Response` class, and is
    used to create a redirect response with a specified location and status
    code.
    The status code is either 301 (Moved Permanently) or 302 (Found), depending
    on the `permanent` parameter.

    The `_encode` method overrides the base class implementation to return an
    empty byte string, since redirect responses typically do not have a
    response body.

    The `__repr__` method returns a string representation of the
    `RedirectResponse` object, including the class name, status line, and
    redirection location.
    """

    __slots__ = ('_body', '_status', '_headers', '_encoded_data')

    def __init__(
        self,
        location: str,
        *,
        body: t.Any = None,
        permanent: bool = False,
        headers: t.Dict[str, t.Any] = {},
    ):
        """
        Initializes a new instance of the `RedirectResponse` class with the
        given location and status code.

        Args:
            `location (str):` The URL to redirect to.
            `permanent (bool, optional):` If True, uses 301 Moved Permanently.
                Otherwise, uses 302 Found.
            `body (Any, optional):` The response body data, generally empty
                for redirects.
            `headers (dict[str, Any], optional):` Additional HTTP headers for
                the response.
        """
        status_code = 301 if permanent else 302
        headers = headers or {}
        headers['location'] = location
        super().__init__(body=body, status_code=status_code, headers=headers)

    def _encode(self) -> bytes:
        """
        Redirection responses typically do not need to encode body data since
        the body is often empty.

        Returns:
            `bytes:` The encoded version of the response body, typically empty
                for redirects.
        """
        return b''

    def __repr__(self) -> str:
        """
        Returns a string representation of the RedirectResponse object.

        The string representation includes the class name, status line, and
        redirection location.

        Returns:
            `str:` The string representation of the RedirectResponse object.
        """
        return f'<{self.__class__.__name__} {self.status_line} {self.header["location"]}>'  # noqa: E501


class FileResponse(Response):
    """
    Represents a file response that can be sent to the client.

    The `FileResponse` class is used to send a file as the response to a
    client request. It handles different types of file input, such as file
    paths, byte strings, and generators, and sets the appropriate headers for
    the file response.

    The class inherits from the `Response` class and adds additional
    attributes and methods specific to file responses, such as the file name,
    attachment status, and encoding of the file data.

    The `_set_headers()` method sets the `content-disposition` header based on
    whether the file should be displayed inline or as an attachment. The
    `_encode()` method handles the encoding of the file data, supporting
    different types of file input.

    The `get_response()` method prepares the complete response data, including
    the encoded file data, status line, and headers.
    """

    default_headers = {'content-type': 'application/octet-stream'}

    __slots__ = (
        '_body',
        '_status',
        '_headers',
        '_encoded_data',
        '_filename',
        '_attachment',
    )

    def __init__(
        self,
        file: t.Union[str, bytes, t.Generator],
        *,
        filename: str,
        attachment: bool = False,
        headers: t.Dict[str, t.Any] = {},
    ):
        """
        Initializes a new instance of the `FileResponse` class.

        Args:
            `file (Union[str, bytes, Generator]):` The file to be included in
                the response. Can be a file path, byte string, or generator.
            `filename (str):` The name of the file to be included in the
                response.
            `attachment (bool, optional):` If True, the file will be sent as an
                attachment. Defaults to False.
            `headers (dict[str, Any], optional):` Additional headers to be
                included in the response. Defaults to an empty dictionary.

        Raises:
            `ValueError:` If the provided file path does not exist.
        """
        super().__init__(body=None, headers=headers)
        self._filename = filename
        self._attachment = attachment

        if isinstance(file, str):
            if not os.path.isabs(file):
                file = os.path.join(os.getcwd(), file)

            if not os.path.isfile(file):
                raise FileNotFound(f'File path {file} does not exist.')

        self._body = file

        self._set_headers()

    def _set_headers(self) -> None:
        """
        Sets the appropriate headers for the file response, including the
        content disposition type (attachment or inline) and the quoted
        filename.
        """
        disposition_type = 'attachment' if self._attachment else 'inline'
        filename_quoted = quote(self._filename)
        self.header['content-disposition'] = (
            f"{disposition_type}; filename*=UTF-8''{filename_quoted}"
        )

    def _encode(self) -> t.Union[bytes, t.Generator[bytes, None, None]]:
        """
        Encodes the file response body based on its type.

        If the body is a string, it is encoded from a file path.
        If the body is bytes, it is returned as-is. If the body is a callable,
        it is called and the result is returned.

        Raises:
            `TypeError:` If the file type is not supported.
        """
        if isinstance(self._body, str):
            return self._encode_from_path(self._body)
        elif isinstance(self._body, bytes):
            return self._body
        elif callable(self._body):
            return self._body()
        else:
            raise UnsupportedBodyType('Unsupported body type.')

    def _encode_from_path(self, path) -> t.Generator[bytes, None, None]:
        """
        Reads the file at the given path in chunks and yields each chunk.

        Args:
            `path (str):` The path to the file to be read.

        Yields:
            `bytes:` The next chunk of the file.

        Raises:
            `TypeError:` If the file type is not supported.
        """
        with open(path, 'rb') as f:
            while chunk := f.read(256 * 1024):
                yield chunk

    def get_response(
        self,
    ) -> t.Tuple[
        t.Union[bytes, t.Generator[bytes, None, None]],
        str,
        t.List[t.Tuple[str, str]],
    ]:
        """
        Returns the encoded file response data, status line, and header list.

        Returns:
            `Tuple[bytes, str, List[Tuple[str, str]]]:` The encoded file
                response data, status line, and header list.
        """
        data = self._encode()
        return (data, self.status_line, self.header_list)
