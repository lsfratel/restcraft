from restipy.core import BaseView, Request, Response


class TestHTTPMethodsView(BaseView):
    route = r'^/$'
    methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'HEAD']

    def handler(self, req: Request) -> Response:
        return Response({'method': req.method[0]})
