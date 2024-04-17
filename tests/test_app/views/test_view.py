from restcraft.core import (
    HTTPException,
    JSONResponse,
    RedirectResponse,
    Request,
    View,
)
from restcraft.core.routing.response import FileResponse, Response
from restcraft.core.routing.utils import url_for


class TestHandlerReturnView(View):
    route = '/test-handler-return'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return {'message': 'this will throw'}  # type: ignore


class TestRaiseHTTPErrorView(View):
    route = '/raise-http-error'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        raise HTTPException('http-error', status_code=422)


class TestMaxBodyView(View):
    route = '/test-max-body'
    methods = ['POST', 'PUT', 'PATCH']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(body=req.json)


class TestRedirectResponseView(View):
    route = '/test-redirect-response'
    methods = ['GET']

    def handler(self, req: Request) -> RedirectResponse:
        return RedirectResponse('/test-redirect-response-target')


class TestRedirectResponseTargetView(View):
    route = '/test-redirect-response-target'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(body={'message': 'hello from redirect'})


class TestFileDownloadView(View):
    route = '/test-file-download'
    methods = ['GET']

    def handler(self, req: Request) -> FileResponse:
        return FileResponse('src/restcraft/wsgi.py', filename='wsgi.py')


class TestRouteParamsView(View):
    route = '/test-route-params/<?age:str>'
    name = 'test-route-params'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        print(url_for('test-route-params', age='123'))
        return JSONResponse(body=req.params)
