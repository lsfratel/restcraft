import importlib
import inspect
import os
import re
import traceback
import typing as t
from types import ModuleType

from restipy.core.exceptions import (
    BaseResponseException,
    InternalServerError,
    RestiPyException,
    RouteNotFoundException,
)
from restipy.core.request import Request
from restipy.core.response import Response
from restipy.routing.router import Route


class RestiPy:
    def __init__(self) -> None:
        self._routes: dict[str, list[Route]] = {}

        self._before_route_m: list[t.Callable] = []
        self._before_m: list[t.Callable] = []
        self._after_m: list[t.Callable] = []

    def bootstrap(self, settings: ModuleType):
        if not hasattr(settings, 'VIEWS'):
            raise RestiPyException('VIEWS setting is missing.')

        if not hasattr(settings, 'MIDDLEWARES'):
            raise RestiPyException('MIDDLEWARES setting is missing.')

        for view in settings.VIEWS:
            self._import_view(view)

        for middleware in settings.MIDDLEWARES:
            self._import_middleware(middleware)

    def _add_route(self, rule: str, method: str, handler: t.Callable) -> None:
        if method.upper() not in self._routes:
            self._routes[method.upper()] = []
        self._routes[method.upper()].append(
            Route(re.compile(rule), method, handler)
        )

    def _import_module(self, filename: str) -> ModuleType:
        if os.path.sep in filename:
            filename = filename.replace(os.path.sep, '.')
        return importlib.import_module(filename)

    def _get_module_members(self, module: ModuleType, mt=inspect.isclass):
        for name, member in inspect.getmembers(module, mt):
            if member.__module__ == module.__name__:
                yield (name, member)

    def _import_view(self, view: str):
        module = self._import_module(view)
        for name, member in self._get_module_members(module):
            instance = member()
            routes = getattr(instance, 'routes')
            if routes is None:
                continue
            for route in routes:
                method, rule, hname = route
                handler = getattr(instance, hname)
                if not handler:
                    raise RestiPyException(
                        f'View {name} is missing {hname} route handler.'
                    )
                self._add_route(rule, method, handler)

    def _import_middleware(self, middleware: str):
        module = self._import_module(middleware)
        for _, member in self._get_module_members(module):
            self.add_middleware(member())

    def add_middleware(self, middleware):
        if hasattr(middleware, 'before_route'):
            self._before_route_m.append(middleware.before_route)

        if hasattr(middleware, 'before_handler'):
            self._before_m.append(middleware.before_handler)

        if hasattr(middleware, 'after_handler'):
            self._after_m.append(middleware.after_handler)

    def match(
        self, path: str, method: str
    ) -> tuple[Route, dict[str, str | t.Any]]:
        methods = [method]
        if method == 'HEAD':
            methods.append('GET')
        for method in methods:
            routes = self._routes.get(method) or []
            for route in routes:
                if match := route.match(path):
                    return route, match.groupdict()
        raise RouteNotFoundException('Route not found.')

    def __call__(
        self, env: dict, start_response: t.Callable
    ) -> t.Iterable[bytes]:
        return self.wsgi(env, start_response)

    def wsgi(self, env: dict, start_response: t.Callable) -> t.Iterable[bytes]:
        method = env.get('REQUEST_METHOD', 'GET').upper()
        out = self.process_request(env)

        data, status, headers = out.get_response()

        start_response(status, headers)

        if method == 'HEAD':
            return []

        return [data]

    def process_request(self, env: dict) -> Response:
        env['restipy.app'] = self
        req = Request(env)

        try:
            for middleware in self._before_route_m:
                resp = middleware(req)
                if isinstance(resp, Response):
                    return resp

            try:
                route, params = self.match(req.path, req.method)
            except RouteNotFoundException as e:
                return e.to_response()

            req.set_params = params

            for middleware in self._before_m:
                resp = middleware(req)
                if isinstance(resp, Response):
                    return resp

            resp = route.handler(req)

            if not isinstance(resp, Response):
                raise InternalServerError(
                    'Handler must return a Response object.'
                )

            for middleware in self._after_m:
                middleware(req, resp)

            return resp
        except BaseResponseException as e:
            return e.to_response()
        except Exception:
            traceback.print_exc()
            stacktrace = traceback.format_exc()
            env['wsgi.errors'].write(stacktrace)
            env['wsgi.errors'].flush()
            return Response({'error': 'Internal Server Error.'}, 500)
