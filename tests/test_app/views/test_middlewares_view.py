from restipy.core import JSONResponse, Request, View


class TestMiddlewareBeforeRouteEarlyReturn(View):
    route = r'^/before-route-early$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'did not return early'})


class TestMiddlewareBeforeHandlerEarlyReturn(View):
    route = r'^/before-handler-early$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'did not return early'})


class TestMiddlewareAfterHandler(View):
    route = r'^/after-handler$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'message': 'message in view'})
