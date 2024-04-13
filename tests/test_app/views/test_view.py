from restipy.core import HTTPException, Request, Response, View


class TestHandlerReturnView(View):
    route = r'^/test-handler-return$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        return {'message': 'this will throw'}  # type: ignore


class TestRaiseHTTPErrorView(View):
    route = r'^/raise-http-error$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        raise HTTPException('http-error', status_code=422)


class TestMaxBodyView(View):
    route = r'^/test-max-body$'
    methods = ['POST', 'PUT', 'PATCH']

    def handler(self, req: Request) -> Response:
        return Response(body=req.json)
