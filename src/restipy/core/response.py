import json
import typing as t

from restipy.core.exceptions import RestiPyException
from restipy.routing import HTTP_CODES, HTTP_STATUS_LINES
from restipy.utils.helpers import pep3333


class BaseResponse:
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
        if self._status in self.bad_headers:
            bad_headers = self.bad_headers[self._status]
            for header in bad_headers:
                if header.lower() in self._headers:
                    del self._headers[header.lower()]
        return [(k, pep3333(v)) for k, v in self._headers.items()]

    @property
    def header(self):
        return self._headers

    @property
    def status(self):
        return self._status

    @property
    def status_line(self):
        return HTTP_STATUS_LINES[self._status]

    @status.setter
    def set_status(self, status: int):
        if status not in HTTP_CODES:
            raise RestiPyException('Invalid status code.')
        self._status = status

    @property
    def data(self):
        return self._body

    @data.setter
    def set_data(self, data: t.Any):
        self._body = data
        self._encoded_data = None

    def _get_encoded_data(self):
        return str(self._body).encode()

    def get_response(self):
        data = self._get_encoded_data()
        self.header['content-length'] = str(len(data))
        status = self.status_line
        headers = self.header_list
        return (data, status, headers)


class Response(BaseResponse):
    default_headers = {'content-type': 'application/json; charset=utf-8'}

    def _get_encoded_data(self):
        return self.json_dumps(self._body).encode()
