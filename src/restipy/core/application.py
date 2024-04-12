import importlib
import inspect
import os
import re
import traceback
import typing as t
from types import ModuleType

from restipy.core.exceptions import HTTPException, RestiPyException
from restipy.core.middleware import BaseMiddleware
from restipy.core.request import Request
from restipy.core.response import Response
from restipy.core.view import BaseView
from restipy.routing.router import Route


class RestiPy:
    def __init__(self) -> None:
        self._routes: dict[str, list[Route]] = {}
        self.config: ModuleType

        self._before_route_m: list[t.Callable] = []
        self._before_m: list[t.Callable] = []
        self._after_m: list[t.Callable] = []

    def bootstrap(self, settings: ModuleType):
        self.config = settings

        for view in settings.VIEWS:
            self._import_view(view)

        for middleware in settings.MIDDLEWARES:
            self._import_middleware(middleware)

    def _add_route(
        self,
        rule: str,
        method: str,
        handler: t.Callable,
        before: t.Callable,
        after: t.Callable,
        on_exception: t.Callable,
    ) -> None:
        method = method.upper()
        if method not in self._routes:
            self._routes[method] = []
        self._routes[method].append(
            Route(
                rule=re.compile(rule),
                method=method,
                handler=handler,
                before=before,
                after=after,
                on_exception=on_exception,
            )
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
        for _, mview in self._get_module_members(module):
            if not issubclass(mview, BaseView):
                continue
            instance = mview()
            route = getattr(instance, 'route', None)
            methods = getattr(instance, 'methods', [])
            if not route or not methods:
                continue
            for method in methods:
                self._add_route(
                    route,
                    method,
                    instance.handler,
                    instance.before,
                    instance.after,
                    instance.on_exception,
                )

    def _import_middleware(self, middleware: str):
        module = self._import_module(middleware)
        for _, member in self._get_module_members(module):
            if not issubclass(member, BaseMiddleware):
                continue
            self.add_middleware(member())

    def add_middleware(self, middleware):
        self._before_route_m.append(middleware.before_route)
        self._before_m.append(middleware.before_handler)
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
        raise HTTPException(
            'Route not found.', status_code=404, code='ROUTE_NOT_FOUND'
        )

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

        yield data

    def process_request(self, env: dict) -> Response:
        env['restipy.app'] = self
        req = Request(env)
        out: Response

        try:
            for middleware in self._before_route_m:
                out = middleware(req)
                if isinstance(out, Response):
                    return out

            route, params = self.match(req.path, req.method)

            req.set_params = params

            for middleware in self._before_m:
                out = middleware(req)
                if isinstance(out, Response):
                    return out

            try:
                out = route.before(req)
                if isinstance(out, Response):
                    return out
                out = route.handler(req)
                if not isinstance(out, Response):
                    raise Exception(
                        'Route handler must return a Response object.'
                    )
                route.after(req, out)
            except RestiPyException as e:
                out = route.on_exception(req, e)
                if not isinstance(out, Response):
                    raise HTTPException(
                        'Route exception must return Response object.',
                        code='HANDLER_EXCEPTION',
                        status_code=500,
                    ) from None
                return out

            for middleware in self._after_m:
                middleware(req, out)

            return out
        except HTTPException as e:
            return Response(
                e.get_response(), status_code=e.status_code, headers=e.headers
            )
        except Exception as e:
            traceback.print_exc()
            stacktrace = traceback.format_exc()
            env['wsgi.errors'].write(stacktrace)
            env['wsgi.errors'].flush()
            if self.config.DEBUG is False:
                return Response(
                    {
                        'code': 'INTERNAL_SERVER_ERROR',
                        'error': 'Something went wrong, try again later.',
                    },
                    status_code=500,
                )
            return Response(
                {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'error': str(e),
                    'stacktrace': stacktrace.splitlines(),
                },
                status_code=500,
            )
