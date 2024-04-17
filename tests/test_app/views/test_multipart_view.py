from restcraft.core import (
    JSONResponse,
    Request,
    View,
)


class TestMultipartFormOnlyView(View):
    route = '/test-multipart-form-only'
    methods = ['POST']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse(req.form)
