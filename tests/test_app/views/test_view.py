from restipy.core.request import Request
from restipy.utils.helpers import re_route
from test_app.exceptions.http_exc import HTTPException


class TestView:
    routes = [
        re_route('GET', r'^/test-handler-return$', 'test_return'),
        re_route('GET', r'^/raise-http-error$', 'raise_http_error'),
        re_route('GET', r'^/raise-exception$', 'raise_exception'),
    ]

    def test_return(self, req: Request):
        return {'message': 'this will throw'}

    def raise_http_error(self, req: Request):
        raise HTTPException('http-error', status_code=422)

    def raise_exception(self, req: Request):
        _ = 1 / 0
