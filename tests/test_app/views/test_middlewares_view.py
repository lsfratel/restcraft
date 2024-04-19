from __future__ import annotations

import typing as t

from restcraft.core import JSONResponse, View

if t.TYPE_CHECKING:
    from restcraft.core import Request


class TestMiddlewareBeforeRouteEarlyReturn(View):
    route = '/before-route-early'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'did not return early'})


class TestMiddlewareBeforeHandlerEarlyReturn(View):
    route = '/before-handler-early'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'did not return early'})


class TestMiddlewareAfterHandler(View):
    route = '/after-handler'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'message in view'})
