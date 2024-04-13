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
    """
    The main class representing the RestiPy application.

    This class provides methods for bootstrapping the application, adding
    routes, importing views and middlewares, matching routes, and handling WSGI
    requests.

    Attributes:
        config (ModuleType): The module containing the application settings.

    Methods:
        bootstrap(settings: ModuleType) -> None:
            Bootstraps the application by setting the configuration, importing
                views, and middleware.

        add_middleware(middleware) -> None:
            Adds a middleware to the application.

        match(path: str, method: str) -> Tuple[Route, Dict[str, str | Any]]:
            Matches the given path and method to a route in the application.

        wsgi(env: dict, start_response: t.Callable) -> t.Iterable[bytes]:
            WSGI application entry point.

        process_request(env: dict) -> Response:
            Process the incoming request and return a response.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the RestiPy class.

        This constructor sets up the internal data structures for managing
        routes, middleware, and configuration.

        Attributes:
            _routes (dict[str, list[Route]]): A dictionary mapping HTTP methods
                to lists of routes.
            config (ModuleType): The module containing the application
                settings.
            _before_route_m (list[Callable]): A list of middleware functions
                to be executed before a route is matched.
            _before_m (list[Callable]): A list of middleware functions to be
                executed before a request is processed.
            _after_m (list[Callable]): A list of middleware functions to be
                executed after a request is processed.
        """
        self._routes: dict[str, list[Route]] = {}
        self.config: ModuleType

        self._before_route_m: list[t.Callable] = []
        self._before_m: list[t.Callable] = []
        self._after_m: list[t.Callable] = []

    def bootstrap(self, settings: ModuleType):
        """
        Bootstraps the application by setting the configuration, importing
        views, and middleware.

        Args:
            settings (ModuleType): The module containing the application
                settings.

        Returns:
            None
        """
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
        """
        Add a route to the application.

        Args:
            rule (str): The URL rule for the route.
            method (str): The HTTP method for the route.
            handler (Callable): The handler function for the route.
            before (Callable): The function to be executed before the handler.
            after (Callable): The function to be executed after the handler.
            on_exception (Callable): The function to be executed on exception.

        Returns:
            None
        """
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
        """
        Import a module given its filename.

        Args:
            filename (str): The filename of the module to import.

        Returns:
            ModuleType: The imported module.
        """
        if os.path.sep in filename:
            filename = filename.replace(os.path.sep, '.')
        return importlib.import_module(filename)

    def _get_module_members(self, module: ModuleType, mt=inspect.isclass):
        """
        Get the members of a module that satisfy a given condition.

        Args:
            module (ModuleType): The module to inspect.
            mt (Callable): The condition that the members should satisfy.
            Defaults to `inspect.isclass`.

        Yields:
            Tuple[str, Any]: A tuple containing the name and member that
                satisfy the condition.
        """
        for name, member in inspect.getmembers(module, mt):
            if member.__module__ == module.__name__:
                yield (name, member)

    def _import_view(self, view: str):
        """
        Import a view module and add its routes to the application.

        Args:
            view (str): The name of the view module to import.

        Returns:
            None
        """
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
        """
        Imports and adds a middleware to the application.

        Args:
            middleware (str): The fully qualified name of the middleware class.

        Returns:
            None
        """
        module = self._import_module(middleware)
        for _, member in self._get_module_members(module):
            if not issubclass(member, BaseMiddleware):
                continue
            self.add_middleware(member())

    def add_middleware(self, middleware):
        """
        Adds a middleware to the application.

        Parameters:
        - middleware: The middleware object to be added.

        This method adds the specified middleware to the application's list of
        middlewares.

        The middleware will be executed in the order they are added, before and
        after the route handlers.
        """
        self._before_route_m.append(middleware.before_route)
        self._before_m.append(middleware.before_handler)
        self._after_m.append(middleware.after_handler)

    def match(
        self, path: str, method: str
    ) -> tuple[Route, dict[str, str | t.Any]]:
        """
        Matches the given path and method to a route in the application.

        Args:
            path (str): The path to match against the routes.
            method (str): The HTTP method to match against the routes.

        Returns:
            tuple[Route, dict[str, str | t.Any]]: A tuple containing the
            matched route and a dictionary of captured
            parameters from the path.

        Raises:
            HTTPException: If no matching route is found.
        """
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
        """
        Handle the WSGI callable interface.

        Args:
            env (dict): The WSGI environment dictionary.
            start_response (callable): The WSGI start_response callable.

        Returns:
            Iterable[bytes]: An iterable of response bytes.
        """
        return self.wsgi(env, start_response)

    def wsgi(self, env: dict, start_response: t.Callable) -> t.Iterable[bytes]:
        """
        Handle the WSGI request and response.

        Args:
            env (dict): The WSGI environment dictionary.
            start_response (callable): The WSGI start_response callable.

        Returns:
            Iterable[bytes]: An iterable of response bytes.
        """
        method = env.get('REQUEST_METHOD', 'GET').upper()
        out = self.process_request(env)

        data, status, headers = out.get_response()

        start_response(status, headers)

        if method == 'HEAD':
            return []

        yield data

    def process_request(self, env: dict) -> Response:
        """
        Process the incoming request and return a response.

        Args:
            env (dict): The WSGI environment dictionary.

        Returns:
            Response: The response object.

        Raises:
            HTTPException: If an HTTP exception occurs.
            Exception: If any other exception occurs.
        """
        env['restipy.app'] = self
        req = Request(env)
        out: Response

        try:
            """
            Process the incoming request through any registered middleware
            before routing the request.

            The middleware is executed in the order they were registered.
            If any middleware returns a `Response` object, the request
            processing is short-circuited and the response is returned
            immediately.

            Args:
                req (Request): The incoming request object.

            Returns:
                Response: The response object, if a middleware returned one.
            """
            for middleware in self._before_route_m:
                out = middleware(req)
                if isinstance(out, Response):
                    return out

            """
            Match the incoming request path and HTTP method to a registered
            route.

            Args:
                req (Request): The incoming request object.

            Returns:
                Tuple[Route, dict]: The matched route and any extracted
                    parameters from the path.
            """
            route, params = self.match(req.path, req.method)

            req.set_params = params

            """
            Process the incoming request through any registered middleware
            before routing the request.

            The middleware is executed in the order they were registered.
            If any middleware returns a `Response` object, the request
            processing is short-circuited and the response is returned
            immediately.

            Args:
                req (Request): The incoming request object.

            Returns:
                Response: The response object, if a middleware returned one.
            """
            for middleware in self._before_m:
                out = middleware(req)
                if isinstance(out, Response):
                    return out

            """
            Process the incoming request through the registered view.

            This block of code is responsible for executing the before,
            handler, and after hooks of the matched view. If any of these
            hooks return a `Response` object, the request processing is
            short-circuited and the response is returned immediately.

            If the view handler does not return a `Response` object, an
            exception is raised. If a `RestiPyException` is raised during the
            request processing, the `on_exception` hook of the view is
            executed, and the returned response is returned.
            """
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

            """
            Execute the registered after middleware.

            The middleware is executed in the order they were registered.
            If any middleware returns a `Response` object, the request
            processing is short-circuited and the response is returned
            immediately.

            Args:
                req (Request): The incoming request object.
                out (Response): The response object returned by the view
                    handler.
            """
            for middleware in self._after_m:
                middleware(req, out)

            return out
        except HTTPException as e:
            return Response(
                e.get_response(), status_code=e.status_code, headers=e.headers
            )
        except Exception as e:
            """
            Handles an unhandled exception that occurred during the request
            processing.

            This code block is executed when an unhandled exception occurs
            during the request processing. It logs the exception traceback to
            the WSGI error stream, and returns a JSON response with an error
            message and the exception traceback.

            If the application is running in debug mode
            (self.config.DEBUG is True), the response will include the full
            exception traceback. Otherwise, a generic "Something went wrong,
            try again later" error message is returned.

            Args:
                e (Exception): The unhandled exception that occurred.

            Returns:
                Response: A JSON response with an error message and, if in
                    debug mode, the exception traceback.
            """
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
