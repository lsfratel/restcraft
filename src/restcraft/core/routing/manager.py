import re
import typing as t
from functools import cache

from ..exceptions import RouteNotFound
from .route import Route
from .types import (
    FloatType,
    IntType,
    ParamType,
    SlugType,
    StringType,
    UUIDType,
)
from .view import View


class RouteManager:
    def __init__(self):
        self._routes: t.Dict[str, t.List[Route]] = {}

        self._view_name_mapping: t.Dict[str, str] = {}

        self._route_type_mapping: t.Dict[str, t.Type[ParamType]] = {
            'default': StringType,
            'int': IntType,
            'float': FloatType,
            'str': StringType,
            'slug': SlugType,
            'uuid': UUIDType,
        }

    def _validate_pattern(self, pattern: str):
        """
        Validates the pattern of a route by checking the following:
        - Ensures that there is only one parameter per segment of the route
          path.
        - Checks that static segments of the route path only contain
          alphanumeric characters, dashes, and underscores.
        - Verifies that any defined parameter types are valid according to the
          `param_types` dictionary.
        - Ensures that parameter names are alphanumeric and can include
          underscores but not dashes.
        """
        segments = pattern.strip('/').split('/')

        for segment in segments:
            if re.search(r'<[^>]+>.*<[^>]+>', segment):
                raise ValueError(
                    'Multiple params in one segment are not supported.'
                )

            static_parts = re.split(r'<[^>]+>', segment)
            for part in static_parts:
                if part and not re.match(r'^[\w-]*$', part):
                    raise ValueError(
                        'Static segments must only contain alphanumeric '
                        'characters, dashes (-), and underscores (_).'
                    )

            params = re.findall(r'<([^>]+)>', segment)
            for param in params:
                if ':' in param:
                    param_name, param_type = param.split(':')
                    if param_type not in self._route_type_mapping:
                        raise ValueError(
                            f"Parameter type '{param_type}' is not defined."
                        )
                else:
                    param_name = param

                if not re.match(r'^[\w?]*$', param_name):
                    raise ValueError(
                        'Parameter names should be alphanumeric and can '
                        'include underscores but not dashes.'
                    )

    def _parse_segment(
        self, segment: str
    ) -> t.Tuple[str, t.List[t.Tuple[str, t.Type[ParamType], bool]]]:
        """
        Parses a route segment and extracts any named parameters and their
        types.

        Args:
            segment (str): The route segment to parse.

        Returns:
            Tuple[str, List[Tuple[str, Type, bool]]]: A tuple containing the
                modified segment with parameter placeholders replaced by regex
                patterns, and a list of tuples containing the parameter name,
                type, and whether the parameter is optional.
        """
        pattern_param = re.compile(r'<(\??)([^>:]+)(?::([^>]+))?>')
        matches = pattern_param.findall(segment)

        if not matches:
            return (f'/{segment}', [])

        param_names: t.List[t.Tuple[str, t.Type[ParamType], bool]] = []
        modified_segment = segment

        for optional, param_name, param_type_key in matches:
            is_optional: bool = optional == '?'
            param_type = self._route_type_mapping.get(
                param_type_key or 'default',
                self._route_type_mapping['default'],
            )
            regex_formatted = (
                param_type.pattern
                if not is_optional
                else f'{param_type.pattern}?'
            )
            param_names.append((param_name, param_type, is_optional))
            placeholder = (
                f'<{optional}{param_name}'
                f'{":" + param_type_key if param_type_key else ""}>'
            )
            segment_part = (
                f'/{regex_formatted}'
                if not is_optional
                else f'(?:/{regex_formatted})?'
            )
            modified_segment = modified_segment.replace(
                placeholder, segment_part, 1
            )

        return modified_segment, param_names

    def _parse_pattern(
        self,
        pattern: str,
    ) -> t.Tuple[str, t.List[t.Tuple[str, t.Type[ParamType], bool]]]:
        """
        Parses the route pattern and extracts the regular expression and
        parameter names.

        The route pattern is split into segments, and each segment is parsed
        to extract a regular expression part and any parameter names.
        The regular expression parts are then joined together to form the full
        regular expression pattern, and the parameter names are collected.

        The resulting regular expression pattern and parameter names are
        returned.
        """
        segments = pattern.strip('/').split('/')
        regex_parts = []
        param_names: t.List[t.Tuple[str, t.Type[ParamType], bool]] = []

        for segment in segments:
            regex_part, segment_param_names = self._parse_segment(segment)
            regex_parts.append(regex_part)
            param_names.extend(segment_param_names)

        full_regex = ''.join(regex_parts)
        full_regex = f'^{full_regex}/?$' if full_regex.strip('/') else '^/$'

        return full_regex, param_names

    def add_type(
        self, name: str, type: t.Type[ParamType], reaplce: bool = False
    ):
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
        if name in self._route_type_mapping and not reaplce:
            raise ValueError(f'Type with name {name} already exists.')

        self._route_type_mapping[name] = type

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

        self._validate_pattern(view.route)

        regex, params = self._parse_pattern(view.route)

        if isinstance(regex, str):
            regex = re.compile(regex)

        route = Route(view=view, regex=regex, params=params)

        if hasattr(view, 'name'):
            if view.name in self._view_name_mapping:
                raise ValueError(
                    f'A view with the name {view.name} already exists.'
                )

            self._view_name_mapping[view.name] = view.route

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


route_manager = RouteManager()
