from restipy.core.request import Request
from restipy.core.response import Response
from restipy.utils.helpers import re_route


class TestView:
    routes = [
        re_route('GET', r'^/$', 'on_get'),
        re_route('POST', r'^/$', 'on_post'),
        re_route('PATCH', r'^/$', 'on_patch'),
        re_route('PUT', r'^/$', 'on_put'),
        re_route('DELETE', r'^/$', 'on_delete'),
    ]

    def on_get(self, req: Request) -> Response:
        return Response({'message': 'test method'})

    def on_post(self, req: Request) -> Response:
        return Response({'message': 'test method'})

    def on_patch(self, req: Request) -> Response:
        return Response({'message': 'test method'})

    def on_put(self, req: Request) -> Response:
        return Response({'message': 'test method'})

    def on_delete(self, req: Request) -> Response:
        return Response({'message': 'test method'})
