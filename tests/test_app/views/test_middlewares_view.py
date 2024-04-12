from restipy.core import BaseView, Request, Response


class TestMiddlewareBeforeRouteEarlyReturn(BaseView):
    route = r'^/before-route-early$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        return Response({'message': 'did not return early'})


class TestMiddlewareBeforeHandlerEarlyReturn(BaseView):
    route = r'^/before-handler-early$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        return Response({'message': 'did not return early'})


class TestMiddlewareAfterHandler(BaseView):
    route = r'^/after-handler$'
    methods = ['GET']

    def handler(self, req: Request) -> Response:
        return Response({'message': 'message in view'})
