from restipy.core import (
    HTTPException,
    JSONResponse,
    RedirectResponse,
    Request,
    View,
)
from restipy.core.response import FileResponse


class TestHandlerReturnView(View):
    route = r'^/test-handler-return$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return {'message': 'this will throw'}  # type: ignore


class TestRaiseHTTPErrorView(View):
    route = r'^/raise-http-error$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        raise HTTPException('http-error', status_code=422)


class TestMaxBodyView(View):
    route = r'^/test-max-body$'
    methods = ['POST', 'PUT', 'PATCH']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(body=req.json)


class TestRedirectResponseView(View):
    route = r'^/test-redirect-response$'
    methods = ['GET']

    def handler(self, req: Request) -> RedirectResponse:
        return RedirectResponse('/test-redirect-response-target')


class TestRedirectResponseTargetView(View):
    route = r'^/test-redirect-response-target$'
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(body={'message': 'hello from redirect'})


class TestFileDownloadView(View):
    route = r'^/test-file-download$'
    methods = ['GET']

    def handler(self, req: Request) -> FileResponse:
        return FileResponse('src/restipy/wsgi.py', filename='wsgi.py')
