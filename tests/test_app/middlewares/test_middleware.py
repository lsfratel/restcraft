import re

from restipy.core.request import Request
from restipy.core.response import Response


class TestMiddleware:
    rx_before_route = re.compile(r'^/before-route-early$')
    rx_before_handler = re.compile(r'^/before-handler-early$')
    rx_after_handler = re.compile(r'^/after-handler$')

    def before_route(self, req: Request):
        if self.rx_before_route.match(req.path):
            return Response(body={'message': 'early return'})

    def before_handler(self, req: Request) -> Response | None:
        if self.rx_before_handler.match(req.path):
            return Response(body={'message': 'early return'})

    def after_handler(self, req: Request, res: Response):
        if self.rx_after_handler.match(req.path):
            res.set_data = {'message': 'changed in middleware'}
