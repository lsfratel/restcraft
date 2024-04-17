import re
import typing as t

from restcraft.core.routing.types import ParamType
from restcraft.core.view import View


class Route:
    """
    The `Route` class represents a route in the application.

    It encapsulates the view function, parameter types, and the regular
    expression pattern used to match the URL. The class provides methods to
    validate the route pattern, parse the pattern into a regular expression
    and parameter names, and match a given URL against the route.
    """

    __slots__ = ('view', 'param_types', 'param_names', 'regex')

    def __init__(self, view: View, param_types: t.Dict[str, ParamType]):
        self.view = view
        self.param_types = param_types

        self._validate_pattern()

        self.regex, self.param_names = self._parse_pattern()

    def _validate_pattern(self):
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
        segments = self.view.route.strip('/').split('/')
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
                    if param_type not in self.param_types:
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
    ) -> t.Tuple[str, t.List[t.Tuple[str, ParamType, bool]]]:
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

        param_names: t.List[t.Tuple[str, ParamType, bool]] = []
        modified_segment = segment

        for optional, param_name, param_type_key in matches:
            is_optional: bool = optional == '?'
            param_type = self.param_types.get(
                param_type_key or 'default', self.param_types['default']
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
    ) -> t.Tuple[str, t.List[t.Tuple[str, ParamType, bool]]]:
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
        segments = self.view.route.strip('/').split('/')
        regex_parts = []
        param_names: t.List[t.Tuple[str, ParamType, bool]] = []

        for segment in segments:
            regex_part, segment_param_names = self._parse_segment(segment)
            regex_parts.append(regex_part)
            param_names.extend(segment_param_names)

        full_regex = ''.join(regex_parts)
        full_regex = f'^{full_regex}/?$' if full_regex.strip('/') else '^/$'

        return full_regex, param_names

    def match(self, url: str) -> t.Optional[t.Dict[str, t.Any]]:
        """
        Attempts to match the provided URL against the route's regular
        expression pattern, and if successful, returns a dictionary of the
        extracted parameter values.

        Args:
            url (str): The URL to match against the route's pattern.

        Returns:
            Optional[Dict[str, Any]]: If the URL matches the route's pattern,
                a dictionary containing the extracted parameter values is
                returned. Otherwise, `None` is returned.
        """
        match = re.match(self.regex, url)

        if not match:
            return None

        params: t.Dict[str, t.Any] = {}

        for (name, type_, _), value in zip(
            self.param_names, match.groups(), strict=False
        ):
            params[name] = type_.convert(value) if value else None

        return params
