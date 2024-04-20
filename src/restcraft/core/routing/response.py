import json
import os
import types
import typing as t
from http import client as httplib
from urllib.parse import quote

from ...core.exceptions import (
    FileNotFound,
    InvalidStatusCode,
    UnsupportedBodyType,
)
from ...utils.helpers import pep3333

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
    Represents a response object.

    Attributes:
        default_headers (dict): The default headers for the response.
        bad_headers (dict): The headers to be removed for specific status
        codes.
        _body (Any): The response body.
        _status (int): The HTTP status code.
        _headers (dict): The response headers.

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
        Initialize a response object.

        Args:
            body (Any): The response body.
            status_code (int): The HTTP status code.
            headers (dict): The response headers.

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
        Get a list of headers for the response.

        Removes headers specified in `bad_headers` for specific status codes.

        Returns:
            list: The list of headers.

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
        Get the headers for the response.

        Returns:
            dict: The response headers.

        """
        return self._headers

    @property
    def status(self) -> int:
        """
        Get the HTTP status code of the response.

        Returns:
            int: The HTTP status code.

        """
        return self._status

    @property
    def status_line(self) -> str:
        """
        Get the status line for the response.

        Returns:
            str: The status line.

        """
        return _HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int) -> None:
        """
        Set the HTTP status code for the response.

        Args:
            status (int): The HTTP status code.

        Raises:
            InvalidStatusCode: If the status code is not valid.

        """
        if status not in _HTTP_CODES:
            raise InvalidStatusCode()
        self._status = status

    @property
    def body(self) -> t.Any:
        """
        Get the response body.

        Returns:
            Any: The response body.

        """
        return self._body

    @body.setter
    def set_body(self, body: t.Any) -> None:
        """
        Set the response body.

        Args:
            body (Any): The response body.

        """
        self._body = body

    def prepare_response(self):
        """
        Prepare the response body.

        Returns:
            bytes: The prepared response body.

        """
        return (
            bytes()
            if self._body in (None, '', b'')
            else str(self._body).encode()
        )

    def get_response(self) -> t.Tuple[bytes, str, t.List[t.Tuple[str, str]]]:
        """
        Get the response object.

        Returns:
            tuple: The response data.

        """
        data = self.prepare_response()
        self.header['content-length'] = str(len(data))
        status = self.status_line
        headers = self.header_list
        return (data, status, headers)

    def __repr__(self) -> str:
        """
        Return a string representation of the response object.

        Returns:
            str: The string representation of the response object.

        """
        return f'<{self.__class__.__name__} {self.status_line}>'


class JSONResponse(Response):
    """
    Represents a response containing JSON data.

    Attributes:
        default_headers (dict): The default headers for JSON responses,
            containing the content-type as application/json; charset=utf-8.
        _body (Any): The response body.
        _status (int): The HTTP status code.
        _headers (dict): The response headers.
        _encoded_data (bytes): The encoded data for the response.

    """

    default_headers = {'content-type': 'application/json; charset=utf-8'}

    def prepare_response(self) -> bytes:
        """
        Prepare the response body.

        Returns:
            bytes: The prepared response body encoded as JSON.

        """
        return (
            bytes()
            if self._body in (None, '', b'')
            else json.dumps(self._body).encode()
        )


class RedirectResponse(Response):
    """
    Represents a redirect response.

    Args:
        location (str): The URL to redirect to.
        permanent (bool, optional): Whether the redirect is permanent.
            Defaults to False.
        headers (Dict[str, Any], optional): The response headers.
        Defaults to None.

    """

    default_headers = {}

    def __init__(
        self,
        location: str,
        *,
        permanent: bool = False,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        """
        Initialize a RedirectResponse object.

        Args:
            location (str): The URL to redirect to.
            permanent (bool, optional): Whether the redirect is permanent.
                Defaults to False.
            headers (Dict[str, Any], optional): The response headers.
                Defaults to None.

        """
        status_code = 301 if permanent else 302
        headers = headers or {}
        headers['location'] = location
        super().__init__(body=None, status_code=status_code, headers=headers)

    def __repr__(self) -> str:
        """
        Return a string representation of the RedirectResponse object.

        Returns:
            str: The string representation of the RedirectResponse object.

        """
        return (
            f'<{self.__class__.__name__} {self.status_line} '
            f'{self.header["location"]}>'
        )


class FileResponse(Response):
    """
    Represents a response object that contains a file as the body.

    Attributes:
        default_headers (Dict[str, str]): The default headers for the response.
    """

    default_headers = {'content-type': 'application/octet-stream'}

    def __init__(
        self,
        file: t.Union[str, bytes, t.Generator],
        *,
        filename: str,
        attachment: bool = False,
        headers: t.Dict[str, t.Any] = {},
    ):
        """
        Initialize a FileResponse object.

        Args:
            file (Union[str, bytes, Generator]): The file to be used as the
            body.
            filename (str): The name of the file.
            attachment (bool, optional): Whether the file should be downloaded
            as an attachment. Defaults to False.
            headers (Dict[str, Any], optional): The headers for the response.
                Defaults to an empty dictionary.
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
        Set the headers for the response based on the file and attachment
        settings.
        """
        disposition_type = 'attachment' if self._attachment else 'inline'
        filename_quoted = quote(self._filename)
        self.header['content-disposition'] = (
            f"{disposition_type}; filename*=UTF-8''{filename_quoted}"
        )

    def prepare_response(
        self,
    ) -> t.Union[bytes, t.Generator[bytes, None, None]]:
        """
        Prepare the response data based on the file type.

        Returns:
            Union[bytes, Generator[bytes, None, None]]: The response data.

        Raises:
            UnsupportedBodyType: If the file type is unsupported.
        """
        if isinstance(self._body, str):
            return self._generate_file_chunks(self._body)
        elif isinstance(self._body, (bytes, types.GeneratorType)):
            return self._body
        raise UnsupportedBodyType('Unsupported body type.')

    def _generate_file_chunks(
        self, file_path: str
    ) -> t.Generator[bytes, t.Any, None]:
        """
        Generate chunks of the file data.

        Args:
            file_path (str): The path to the file.

        Yields:
            bytes: The chunk of file data.
        """
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(256 * 1024), b''):
                yield chunk

    def get_response(self):
        """
        Get the response data.

        Returns:
            Tuple[Union[bytes, Generator], str, List[Tuple[str, str]]]: The
                response data, status line, and header list.
        """
        return self.prepare_response(), self.status_line, self.header_list

    def __repr__(self) -> str:
        """
        Return a string representation of the FileResponse object.

        Returns:
            str: The string representation of the FileResponse object.

        """
        return (
            f'<{self.__class__.__name__} {self.status_line} '
            f'{self.header["content-disposition"]}>'
        )
