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
    Represents an HTTP response.

    Args:
        body (Any, optional): The response body. Defaults to None.
        status_code (int, optional): The HTTP status code. Defaults to 200.
        headers (Dict[str, Any], optional): The response headers.
            Defaults to None.
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
        status_code: int = 200,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> None:
        """
        Initializes a new instance of the Response class.

        Args:
            body (Any, optional): The response body. Defaults to None.
            status_code (int, optional): The HTTP status code. Defaults to 200.
            headers (Dict[str, Any], optional): The response headers.
                Defaults to None.
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
        Gets the response headers as a list of tuples.

        Returns:
            List[Tuple[str, str]]: The response headers.
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
        Gets the response headers.

        Returns:
            Dict[str, str]: The response headers.
        """
        return self._headers

    @property
    def status(self) -> int:
        """
        Gets the HTTP status code.

        Returns:
            int: The HTTP status code.
        """
        return self._status

    @property
    def status_line(self) -> str:
        """
        Gets the HTTP status line.

        Returns:
            str: The HTTP status line.
        """
        return _HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int) -> None:
        """
        Sets the HTTP status code.

        Args:
            status (int): The HTTP status code.

        Raises:
            InvalidStatusCode: If the status code is invalid.
        """
        if status not in _HTTP_CODES:
            raise InvalidStatusCode()
        self._status = status

    @property
    def body(self) -> t.Any:
        """
        Gets the response body.

        Returns:
            Any: The response body.
        """
        return self._body

    @body.setter
    def set_body(self, body: t.Any) -> None:
        """
        Sets the response body.

        Args:
            body (Any): The response body.
        """
        self._body = body

    def _encode(self) -> bytes:
        """
        Encodes the response body.

        Returns:
            bytes: The encoded response body.
        """
        if self._body is None or self._body == '':
            return b''

        return str(self._body).encode()

    def _get_encoded_data(self) -> bytes:
        """
        Gets the encoded response data.

        Returns:
            bytes: The encoded response data.
        """
        return self._encode()

    def get_response(self) -> t.Tuple[bytes, str, t.List[t.Tuple[str, str]]]:
        """
        Gets the complete HTTP response.

        Returns:
            Tuple[bytes, str, List[Tuple[str, str]]]: The response data,
                status line, and headers.
        """
        data = self._get_encoded_data()
        self.header['content-length'] = str(len(data))
        status = self.status_line
        headers = self.header_list
        return (data, status, headers)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Response object.

        Returns:
            str: The string representation of the Response object.
        """
        return f'<{self.__class__.__name__} {self.status_line}>'


class JSONResponse(Response):
    """
    Represents a JSON response.

    Inherits from the `Response` class and provides functionality to encode
    the response body as JSON.

    Attributes:
        default_headers (dict): Default headers for the JSON response.
    """

    default_headers = {'content-type': 'application/json; charset=utf-8'}

    __slots__ = ('_body', '_status', '_headers', '_encoded_data')

    def _encode(self) -> bytes:
        """
        Encodes the response body as JSON.

        Returns:
            bytes: The encoded JSON data.
        """
        if self._body is None or self._body == '':
            return b''

        return json.dumps(self._body).encode()


class RedirectResponse(Response):
    """
    Represents a redirect response.

    Args:
        location (str): The URL to redirect to.
        body (Any, optional): The response body. Defaults to None.
        permanent (bool, optional): Indicates if the redirect is permanent.
            Defaults to False.
        headers (Dict[str, Any], optional): Additional headers to include in
            the response. Defaults to {}.
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
        status_code = 301 if permanent else 302
        headers = headers or {}
        headers['location'] = location
        super().__init__(body=body, status_code=status_code, headers=headers)

    def _encode(self) -> bytes:
        """
        Encodes the response data into bytes.

        Returns:
            bytes: The encoded response data.
        """
        return b''

    def __repr__(self) -> str:
        """
        Returns a string representation of the Response object.

        The string representation includes the class name, status line,
        and location header.

        Returns:
            str: The string representation of the Response object.
        """
        return f'<{self.__class__.__name__} {self.status_line} {self.header["location"]}>'  # noqa: E501


class FileResponse(Response):
    """
    Represents a response that sends a file to the client.

    Args:
        file (Union[str, bytes, Generator]): The file to be sent. It can be a
            file path, bytes, or a generator function.
        filename (str): The name of the file.
        attachment (bool, optional): Whether the file should be treated as an
            attachment. Defaults to False.
        headers (Dict[str, Any], optional): Additional headers to be included
            in the response. Defaults to {}.
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
        Sets the headers for the response.
        """
        disposition_type = 'attachment' if self._attachment else 'inline'
        filename_quoted = quote(self._filename)
        self.header['content-disposition'] = (
            f"{disposition_type}; filename*=UTF-8''{filename_quoted}"
        )

    def _encode(self) -> t.Union[bytes, t.Generator[bytes, None, None]]:
        """
        Encodes the file body into bytes or a generator.

        Returns:
            Union[bytes, Generator[bytes, None, None]]: The encoded file body.

        Raises:
            UnsupportedBodyType: If the body type is not supported.
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
        Reads and encodes the file from the given path.

        Args:
            path: The path to the file.

        Yields:
            Generator[bytes, None, None]: The encoded file data in chunks.
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
        Gets the response data.

        Returns:
            Tuple[Union[bytes, Generator[bytes, None, None]], str, List[Tuple[str, str]]]:
                The response data, including the encoded file body, status line, and headers.
        """  # noqa: E501
        data = self._encode()
        return (data, self.status_line, self.header_list)
