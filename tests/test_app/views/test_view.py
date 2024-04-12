from restipy.core import BaseView, HTTPException, Request, Response


class TestHandlerReturnView(BaseView):
    route = r'^/test-handler-return$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        return {'message': 'this will throw'}  # type: ignore


class TestRaiseHTTPErrorView(BaseView):
    route = r'^/raise-http-error$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        raise HTTPException('http-error', status_code=422)

    def on_exception(self, req: Request, exc: Exception) -> Response:
        if isinstance(exc, HTTPException):
            return Response(
                exc.get_response(),
                status_code=exc.status_code,
                headers=exc.headers,
            )
        return super().on_exception(req, exc)


class TestMaxBodyView(BaseView):
    route = r'^/test-max-body$'
    methods = ['POST', 'PUT', 'PATCH']

    def handler(self, req: Request) -> Response:
        return Response(body=req.json)

    def on_exception(self, req: Request, exc: Exception) -> Response:
        if isinstance(exc, HTTPException):
            return Response(
                exc.get_response(),
                status_code=exc.status_code,
                headers=exc.headers,
            )
        return super().on_exception(req, exc)
