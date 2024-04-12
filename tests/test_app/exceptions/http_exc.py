import typing as t

from restipy.core import HTTPException


class CustomException(HTTPException):
    code: t.Union[int, str] = 'CUSTOM_EXCEPTION'

    def get_response(self):
        return {
            'code': self.code,
            'error': self.message,
            'custom': 'custom-exception',
        }
