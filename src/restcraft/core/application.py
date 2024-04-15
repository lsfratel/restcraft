import importlib
import inspect
import os
import re
import traceback
import typing as t
from types import ModuleType

from restcraft.conf import settings
from restcraft.core.exceptions import RestCraftException, RouteNotFound
from restcraft.core.middleware import Middleware
from restcraft.core.request import Request
from restcraft.core.response import JSONResponse, Response
from restcraft.core.view import View
from restcraft.utils.helpers import ThreadSafeContext


class RestCraft:
    """
    The RestCraft class is the main entry point for the RestCraft web
    framework. It provides methods for bootstrapping the application, managing
    routes and middleware, and handling WSGI requests.

    The `__init__` method initializes the internal data structures for
    managing routes, middleware, and configuration. The `bootstrap` method
    sets up the application by importing views and middleware.

    The `_add_view` method adds a view to the application's route mapping. The
    `_import_module` and `_get_module_members` methods are utility functions
    for importing modules and getting their members.

    The `_import_view` and `_import_middleware` methods are responsible for
    importing and adding views and middleware to the application, respectively.
    The `add_middleware` method allows adding middleware to the application.

    The `match` method matches the incoming request path and HTTP method to a
    registered route, and returns the matched view and any extracted parameters
    from the path.

    The `__call__` and `wsgi` methods handle the WSGI callable interface,
    processing the incoming request and returning the response.

    The `process_request` method is the core of the request processing logic,
    executing any registered middleware and the matched view's handler.
    """

    __slots__ = ('ctx', '_routes', '_middlewares')

    def __init__(self) -> None:
        """
        Initializes a new instance of the RestCraft class.

        This constructor sets up the internal data structures for managing
        routes and middleware.

        Attributes:
            `ctx (ThreadSafeContext):` The application's context manager.
            `_routes (dict[str, list[Route]]):` A dictionary mapping HTTP
                methods to lists of routes.
            `_before_route_m (list[Callable]):` A list of middleware functions
                to be executed before a route is matched.
            `_before_m (list[Callable]):` A list of middleware functions to be
                executed before a request is processed.
            `_after_m (list[Callable]):` A list of middleware functions to be
                executed after a request is processed.
        """
        self.ctx = ThreadSafeContext()

        self._routes: t.Dict[str, t.List[View]] = {}

        self._middlewares: t.List[Middleware] = []

    def bootstrap(self) -> None:
        """
        Bootstraps the application by importing views, and middleware.
        """
        for view in settings.VIEWS:
            self._import_view(view)

        for middleware in settings.MIDDLEWARES:
            self._import_middleware(middleware)

    def _add_view(self, view: View) -> None:
        """
        Adds a view to the application's routing table.

        Args:
            `view (View):` The view to be added.

        This method compiles the route pattern in the view, and then adds the
        view to the appropriate list of routes based on the HTTP methods it
        supports. If a list of routes for a particular HTTP method does not
        yet exist, it is created.
        """
        if not isinstance(view.route, str):
            view.route = re.compile(view.route)

        for method in view.methods:
            method = method.upper()
            if method not in self._routes:
                self._routes[method] = []
            self._routes[method].append(view)

    def _import_module(self, path: str) -> t.Union[ModuleType, t.Any]:
        """
        Import a module given its filename.

        Args:
            `filename (str):` The filename of the module to import.

        Returns:
            `ModuleType:` The imported module.
        """
        if os.path.sep in path:
            module_path = path.replace(os.path.sep, '.')

        try:
            obj = importlib.import_module(path)
        except ModuleNotFoundError:
            module_path, _, attribute_name = path.rpartition('.')
            if attribute_name:
                module = importlib.import_module(module_path)
                obj = getattr(module, attribute_name)
            else:
                raise

        return obj

    def _get_module_members(
        self, module: ModuleType, mt=inspect.isclass
    ) -> t.Generator[t.Tuple[str, t.Any], None, None]:
        """
        Get the members of a module that satisfy a given condition.

        Args:
            `module (ModuleType):` The module to inspect.
            `mt (Callable):` The condition that the members should satisfy.
                Defaults to `inspect.isclass`.

        Yields:
            `Tuple[str, Any]:` A tuple containing the name and member that
                satisfy the condition.
        """
        for name, member in inspect.getmembers(module, mt):
            if member.__module__ == module.__name__:
                yield (name, member)

    def _import_view(self, path: str) -> None:
        """
        Import a view module and add its routes to the application.

        Args:
            `path (str):` The name of the view module to import.
        """

        result = self._import_module(path)

        if inspect.isclass(result):
            if not issubclass(result, View):
                raise TypeError(f'View {path} must be a subclass of View.')
            self._add_view(result(self))
        else:
            for _, view in self._get_module_members(result):
                if not issubclass(view, View):
                    continue
                self._add_view(view(self))

    def _import_middleware(self, path: str) -> None:
        """
        Imports and adds a middleware to the application.

        Args:
            `path (str):` The fully qualified name of the middleware
                class.
        """

        result = self._import_module(path)

        if inspect.isclass(result):
            if not issubclass(result, Middleware):
                raise TypeError(
                    f'Middleware {path} must be a subclass of Middleware.'
                )
            self.add_middleware(result(self))
        else:
            for _, middleware in self._get_module_members(result):
                if not issubclass(middleware, Middleware):
                    continue
                self.add_middleware(middleware(self))

    def add_middleware(self, middleware: Middleware) -> None:
        """
        Adds a middleware to the application.

        Args:
            `middleware:` The middleware object to be added.

        This method adds the specified middleware to the application's list of
        middlewares.

        The middleware will be executed in the order they are added, before and
        after the route handlers.
        """
        self._middlewares.append(middleware)

    def match(
        self, path: str, method: str
    ) -> t.Tuple[View, t.Dict[str, str | t.Any]]:
        """
        Matches the given path and method to a route in the application.

        Args:
            `path (str):` The path to match against the routes.
            `method (str):` The HTTP method to match against the routes.

        Returns:
            `tuple[Route, dict[str, str | t.Any]]:` A tuple containing the
                matched route and a dictionary of captured parameters from
                the path.

        Raises:
            `RouteNotFound:` If no matching route is found.
        """
        methods = [method]

        if method == 'HEAD':
            methods.append('GET')

        for method in methods:
            routes = self._routes.get(method) or []
            for view in routes:
                if isinstance(view.route, str):
                    view.route = re.compile(view.route)

                if match := view.route.match(path):
                    return view, match.groupdict()

        raise RouteNotFound('Route not found.')

    def __call__(
        self, env: t.Dict, start_response: t.Callable
    ) -> t.Iterable[bytes]:
        """
        Handle the WSGI callable interface.

        Args:
            `env (dict):` The WSGI environment dictionary.
            `start_response (callable):` The WSGI start_response callable.

        Returns:
            `Iterable[bytes]:` An iterable of response bytes.
        """
        return self.wsgi(env, start_response)

    def wsgi(
        self, env: t.Dict, start_response: t.Callable
    ) -> t.Iterable[bytes]:
        """
        Handle the WSGI request and response.

        Args:
            `env (dict):` The WSGI environment dictionary.
            `start_response (callable):` The WSGI start_response callable.

        Returns:
            `Iterable[bytes]:` An iterable of response bytes.
        """
        method = env.get('REQUEST_METHOD', 'GET').upper()

        data, status, headers = self.process_request(env)

        start_response(status, headers)

        if method == 'HEAD':
            data = bytes()

        if inspect.isgenerator(data):
            yield from data
        else:
            yield data

    def process_request(
        self, env: t.Dict
    ) -> t.Tuple[bytes, str, t.List[t.Tuple[str, str]]]:
        """
        Process the incoming request and return a response.

        Args:
            `env (dict):` The WSGI environment dictionary.

        Returns:
            `Response:` The response object.

        Raises:
            `HTTPException:` If an HTTP exception occurs.
            `Exception:` If any other exception occurs.
        """
        env['restcraft.app'] = self
        self.ctx.request = req = Request(env)

        try:
            """
            Iterates through the registered middleware components and calls
            the `before_route` method on each one.

            If any middleware component returns a `Response` object, it is
            immediately returned, short-circuiting the request processing.
            """
            for middleware in self._middlewares:
                early = middleware.before_route(req)
                if isinstance(early, Response):
                    return early.get_response()

            """
            Match the incoming request path and HTTP method to a registered
            route.
            """
            view, params = self.match(req.path, req.method)

            self.ctx.view = view

            req.set_params = params

            """
            Iterates through the registered middleware components and calls
            the `before_handler` method on each one.

            If any middleware component returns a `Response` object, it is
            immediately returned, short-circuiting the request processing.
            """
            for middleware in self._middlewares:
                early = middleware.before_handler(req)
                if isinstance(early, Response):
                    return early.get_response()

            """
            Process the incoming request through the registered view.

            This block of code is responsible for executing the before,
            handler, and after hooks of the matched view. If any of these
            hooks return a `Response` object, the request processing is
            short-circuited and the response is returned immediately.

            If the view handler does not return a `Response` object, an
            exception is raised. If a `RestCraftException` is raised during the
            request processing, the `on_exception` hook of the view is
            executed, and the returned response is returned.
            """
            try:
                early = view.before_handler(req)
                if isinstance(early, Response):
                    return early.get_response()
                out = view.handler(req)
                if not isinstance(out, Response):
                    raise RestCraftException(
                        'Route handler must return a Response object.'
                    )
                view.after_handler(req, out)
            except RestCraftException as e:
                out = view.on_exception(req, e)
                if not isinstance(out, Response):
                    raise RestCraftException(
                        'Route exception must return Response object.'
                    ) from e
                return out.get_response()

            """
            Iterates through the registered middleware components and calls
            the `after_handler` method on each one.

            This method is called after the view handler has executed and
            returned a response. It allows middleware components to perform
            any necessary post-processing or cleanup tasks before the response
            is returned to the client.
            """
            for middleware in self._middlewares:
                middleware.after_handler(req, out)

            """
            Returns the final response object after all middleware components
            have performed any necessary post-processing or cleanup tasks.
            """
            return out.get_response()
        except RestCraftException as e:
            if settings.DEBUG:
                e.payload = {
                    'details': {
                        'exception': e.message,
                        'stacktrace': traceback.format_exc().splitlines(),
                    }
                }

            out = JSONResponse(
                e.to_response(), status_code=e.status_code, headers=e.headers
            )
            return out.get_response()
        except Exception as e:
            """
            Handles an unhandled exception that occurred during the request
            processing.

            This code block is executed when an unhandled exception occurs
            during the request processing. It logs the exception traceback to
            the WSGI error stream, and returns a JSON response with an error
            message and the exception traceback.

            If the application is running in debug mode
            (settings.DEBUG is True), the response will include the full
            exception traceback. Otherwise, a generic "Something went wrong,
            try again later" error message is returned.

            Args:
                `e (Exception):` The unhandled exception that occurred.

            Returns:
                `Response:` A JSON response with an error message and, if in
                    debug mode, the exception traceback.
            """
            traceback.print_exc()
            stacktrace = traceback.format_exc()
            env['wsgi.errors'].write(stacktrace)
            env['wsgi.errors'].flush()

            exc_body: t.Dict = {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Something went wrong, try again later.',
            }

            if settings.DEBUG:
                exc_body['details'] = {
                    'exception': str(e),
                    'stacktrace': stacktrace.splitlines(),
                }

            out = JSONResponse(exc_body, status_code=500)

            return out.get_response()
        finally:
            """
            Clears the context associated with the current request.
            """
            self.ctx.clear()
