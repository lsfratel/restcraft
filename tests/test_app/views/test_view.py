from __future__ import annotations

import typing as t

from restcraft.core import (
    FileResponse,
    HTTPException,
    JSONResponse,
    RedirectResponse,
    View,
)
from restcraft.core.di import inject

from tests.test_app.services.transient import MyTransientService

if t.TYPE_CHECKING:
    from restcraft.core import Request


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
    methods = ['GET']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(body=req.params)


class TestDIView(View):
    route = '/test-di'
    methods = ['GET']

    @inject
    def handler(
        self, req: Request, logger: MyTransientService
    ) -> JSONResponse:
        return JSONResponse(
            body={'message': logger.return_msg('heelo from di')}
        )
