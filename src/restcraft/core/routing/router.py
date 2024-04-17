import typing as t
from functools import cache

from restcraft.core.exceptions import RouteNotFound
from restcraft.core.routing.route import Route
from restcraft.core.routing.types import (
    FloatType,
    IntType,
    ParamType,
    SlugType,
    StringType,
    UUIDType,
)
from restcraft.core.view import View

_type_map: t.Dict[str, ParamType] = {
    'default': StringType,
    'int': IntType,
    'float': FloatType,
    'str': StringType,
    'slug': SlugType,
    'uuid': UUIDType,
}  # type: ignore

_url_registry: t.Dict[str, str] = {}


class Router:
    """
    The `Router` class is responsible for managing the routing of HTTP requests
    to the appropriate views. It provides methods for adding routes, parsing
    paths, and resolving the correct route for a given HTTP method and path.

    The `add_type` method allows custom parameter types to be registered with
    the router, which can be used in route definitions.

    The `add_route` method adds a new route to the router, associating it with
    the specified view.

    The `parse_path` method takes a route path string and returns a regular
    expression, a dictionary of parameter types, and a list of parameter names.

    The `resolve` method takes an HTTP method and a path, and returns the
    matching route and its parameters.
    """

    def __init__(self):
        self._routes: t.Dict[str, t.List[Route]] = {}
        self._type_map = _type_map
        self._url_registry = _url_registry

    def add_type(self, name: str, type: ParamType, reaplce: bool = False):
        """
        Adds a custom parameter type to the router.

        Args:
            name (str): The name of the custom parameter type.
            type (ParamType): The custom parameter type to register.
            replace (bool, optional): If True, replaces an existing type with
                the same name. Defaults to False.

        Raises:
            ValueError: If a type with the given name already exists and
                `replace` is False.
        """
        if name in self._type_map and not reaplce:
            raise ValueError(f'Type with name {name} already exists.')

        self._type_map[name] = type

    def add_route(self, view: View):
        """
        Adds a new route to the router, associating it with the specified view.

        Args:
            view (View): The view to associate with the new route.

        The method parses the path of the view to extract a regular expression,
        parameter types, and parameter names. It then creates a new `Route`
        object with this information and adds it to the list of routes for the
        corresponding HTTP method in the `_routes` dictionary.
        """
        route = Route(view, self._type_map)

        if hasattr(view, 'name'):
            if view.name in self._url_registry:
                raise ValueError(
                    f'A view with the name {view.name} already exists.'
                )

            self._url_registry[view.name] = view.route

        for method in view.methods:
            routes = self._routes.setdefault(method.upper(), [])
            routes.append(route)

    @cache
    def resolve(self, method: str, path: str):
        """
        Resolves the appropriate route for the given HTTP method and path.

        Args:
            method (str): The HTTP method (e.g. "GET", "POST", "DELETE").
            path (str): The path to resolve
                (e.g. "/users/1", "/products/search").

        Returns:
            Tuple[Route, Dict[str, Any]]: A tuple containing the matched Route
                and a dictionary of the extracted path parameters.

        Raises:
            RouteNotFound: If no route matches the given method and path.
        """
        method = method.upper()

        if method not in self._routes:
            raise RouteNotFound('No route matches the given URL.')

        for route in self._routes[method]:
            params = route.match(path)

            if params is None:
                continue

            return route, params

        raise RouteNotFound('No route matches the given URL.')
