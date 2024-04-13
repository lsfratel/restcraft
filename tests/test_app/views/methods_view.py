from restipy.core import Request, Response, View


class TestHTTPMethodsView(View):
    route = r'^/$'
    methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'HEAD']

    def handler(self, req: Request) -> Response:
        return Response({'method': req.method[0]})
