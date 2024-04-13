import json
import typing as t

from restipy.core.exceptions import RestiPyException
from restipy.routing import HTTP_CODES, HTTP_STATUS_LINES
from restipy.utils.helpers import pep3333


class BaseResponse:
    """
    Represents a base response object for HTTP responses.

    Attributes:
        _body (Any): The response body.
        _status (int): The response status code.
        _headers (dict[str, Any]): The response headers.
        _encoded_data (bytes): The encoded response data.
        json_dumps (Callable): The JSON serialization function.
        json_loads (Callable): The JSON deserialization function.

    Properties:
        header_list (List[Tuple[str, str]]): The list of response headers.
        header (dict[str, Any]): The response headers.
        status (int): The response status code.
        status_line (str): The response status line.
        data (Any): The response body.

    Methods:
        set_status(status: int): Sets the response status code.
        set_data(data: Any): Sets the response body.
        get_response() -> Tuple[bytes, str, List[Tuple[str, str]]]: Returns
            the encoded response data, status line, and headers.

    """

    __slots__ = (
        '_body',
        '_status',
        '_headers',
        '_encoded_data',
        'json_dumps',
        'json_loads',
    )

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
        self._body = body
        self._status = status_code
        self._headers = self.default_headers.copy()
        self.json_dumps = json.dumps
        self.json_loads = json.loads
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
            list: A list of tuples representing the headers in the response.
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

        :return: The headers of the response.
        """
        return self._headers

    @property
    def status(self):
        """
        Returns the status of the response.

        :return: The status of the response.
        """
        return self._status

    @property
    def status_line(self):
        """
        Returns the status line corresponding to the current status code.

        :return: The status line as a string.
        """
        return HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int):
        """
        Sets the status code for the response.

        Args:
            status (int): The HTTP status code to set.

        Raises:
            RestiPyException: If the provided status code is invalid.
        """
        if status not in HTTP_CODES:
            raise RestiPyException('Invalid status code.')
        self._status = status

    @property
    def data(self):
        """
        Returns the body of the response.

        Returns:
            The body of the response.
        """
        return self._body

    @data.setter
    def set_data(self, data: t.Any):
        """
        Set the data for the response body.

        Args:
            data (Any): The data to be set as the response body.

        Returns:
            None
        """
        self._body = data
        self._encoded_data = None

    def _get_encoded_data(self):
        """
        Returns the encoded version of the response body.

        Returns:
            bytes: The encoded version of the response body.
        """
        return str(self._body).encode()

    def get_response(self):
        """
        Returns the response data, status line, and headers as a tuple.

        :return: A tuple containing the response data, status line, and
        headers.
        :rtype: tuple
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
            str: The string representation of the Response object.
        """
        return f'<{self.__class__.__name__} {self.status_line}>'


class Response(BaseResponse):
    default_headers = {'content-type': 'application/json; charset=utf-8'}

    def _get_encoded_data(self):
        return self.json_dumps(self._body).encode()
