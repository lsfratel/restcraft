from restipy.core.request import Request
from restipy.core.response import Response
from restipy.utils.helpers import re_route


class TestView:
    routes = [
        re_route('GET', r'^/before-route-early$', 'on_early'),
        re_route('GET', r'^/before-handler-early$', 'on_early'),
        re_route('GET', r'^/after-handler$', 'after_handler'),
    ]

    def on_early(self, req: Request) -> Response:
        return Response({'message': 'did not return early'})

    def after_handler(self, req: Request) -> Response:
        return Response({'message': 'message in view'})
