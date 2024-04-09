import typing as t

from restipy.core.exceptions import BaseResponseException
from restipy.core.response import Response


class HTTPException(BaseResponseException):
    code: t.Union[int, str] = 'HTTP_EXCEPTION'

    def to_response(self):
        return Response(
            body={'code': self.code, 'error': self.message},
            status=self.status_code,
            headers=self.headers,
        )
