from restcraft.core import JSONResponse, Request, View


class TestHTTPMethodsView(View):
    route = '/'
    methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'HEAD']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'method': req.method[0]})
