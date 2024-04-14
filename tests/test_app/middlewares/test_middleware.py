import re

from restcraft.core import JSONResponse, Request
from restcraft.core.middleware import Middleware


class TestMiddleware(Middleware):
    rx_before_route = re.compile(r'^/before-route-early$')
    rx_before_handler = re.compile(r'^/before-handler-early$')
    rx_after_handler = re.compile(r'^/after-handler$')

    def before_route(self, req: Request):
        if self.rx_before_route.match(req.path):
            return JSONResponse(body={'message': 'early return'})

    def before_handler(self, req: Request) -> JSONResponse | None:
        if self.rx_before_handler.match(req.path):
            return JSONResponse(body={'message': 'early return'})

    def after_handler(self, req: Request, res: JSONResponse):
        if self.rx_after_handler.match(req.path):
            res.set_body = {'message': 'changed in middleware'}
