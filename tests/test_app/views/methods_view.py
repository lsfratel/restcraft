from restipy.core import JSONResponse, Request, View


class TestHTTPMethodsView(View):
    route = r'^/$'
    methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'HEAD']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'method': req.method[0]})
