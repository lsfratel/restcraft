from __future__ import annotations

import typing as t

from restcraft.conf import settings
from restcraft.core.middleware import Middleware
from restcraft.core.request import Request
from restcraft.core.response import Response

if t.TYPE_CHECKING:
    from restcraft.core.application import RestCraft


class CORSMiddleware(Middleware):
    """
    Middleware class for handling Cross-Origin Resource Sharing (CORS) headers.
    """

    def __init__(self, app: RestCraft) -> None:
        """
        Initializes the CORSMiddleware instance.

        Args:
            app (RestCraft): The RestCraft application instance.
        """
        super().__init__(app)
        self.origins = settings.CORS.get('origin')
        self.methods = settings.CORS.get('methods')
        self.headers = settings.CORS.get('headers')
        self.credentials = settings.CORS.get('credentials')
        self.exposed_headers = settings.CORS.get('exposed_headers')
        self.max_age = settings.CORS.get('max_age')

    def configure_headers(
        self, header_key: str, header_type: str
    ) -> t.Dict[str, str]:
        """
        Configures the CORS headers based on the specified header key and type.

        Args:
            header_key (str): The key of the header to configure.
            header_type (str): The type of the header to configure.

        Returns:
            Dict[str, str]: A dictionary containing the configured header.
        """
        header_value = getattr(self, header_type, None)
        if not header_value:
            return {}
        if header_value == '*' or '*' in header_value:
            return {header_key: '*'}
        return {header_key: ', '.join(header_value)}

    def configure_credentials(self) -> t.Dict[str, str]:
        """
        Configures the 'Access-Control-Allow-Credentials' header.

        Returns:
            Dict[str, str]: A dictionary containing the configured header.
        """
        if self.credentials:
            return {'Access-Control-Allow-Credentials': 'true'}
        return {}

    def configure_maxage(self) -> t.Dict[str, str]:
        """
        Configures the 'Access-Control-Max-Age' header.

        Returns:
            Dict[str, str]: A dictionary containing the configured header.
        """
        if self.credentials is not None:
            return {'Access-Control-Max-Age': str(self.credentials)}
        return {}

    def is_allowed_origin(
        self, origin: str, allowed_origin: t.Union[str, t.List[str]]
    ) -> bool:
        """
        Checks if the specified origin is allowed based on the allowed origins.

        Args:
            origin (str): The origin to check.
            allowed_origin (Union[str, List[str]]): The allowed origin(s).

        Returns:
            bool: True if the origin is allowed, False otherwise.
        """
        if isinstance(allowed_origin, str):
            return origin.lower() == allowed_origin.lower()
        return origin.lower() in [ao.lower() for ao in allowed_origin]

    def configure_origin(self, req: Request):
        """
        Configures the 'Access-Control-Allow-Origin' header based on the
        request origin.

        Args:
            req (Request): The incoming request.

        Returns:
            Dict[str, str]: A dictionary containing the configured header.
        """
        req_origin = req.origin
        header = {}

        if not self.origins or self.origins == '*' or '*' in self.origins:
            header['Access-Control-Allow-Origin'] = '*'
        elif isinstance(self.origins, str):
            if self.is_allowed_origin(req_origin, self.origins):
                header['Access-Control-Allow-Origin'] = self.origins
                header['Vary'] = 'Origin'
            else:
                header['Access-Control-Allow-Origin'] = 'null'
        else:
            if self.is_allowed_origin(req_origin, self.origins):
                header['Access-Control-Allow-Origin'] = req_origin
                header['Vary'] = 'Origin'
            else:
                header['Access-Control-Allow-Origin'] = 'null'

        return header

    def before_route(self, req: Request) -> t.Optional[Response]:
        """
        Handles the CORS headers before routing the request.

        Args:
            req (Request): The incoming request.

        Returns:
            Optional[Response]: A response if the request is an OPTIONS
                request, None otherwise.
        """
        origin_headers = self.configure_origin(req)

        if origin_headers['Access-Control-Allow-Origin'] == 'null':
            return Response(status_code=403)

        headers = {
            **origin_headers,
            **self.configure_headers(
                'Access-Control-Allow-Methods', 'methods'
            ),
            **self.configure_credentials(),
            **self.configure_headers(
                'Access-Control-Allow-Headers', 'headers'
            ),
            **self.configure_headers(
                'Access-Control-Expose-Headers', 'exposed_headers'
            ),
            **self.configure_maxage(),
        }

        if req.method == 'OPTIONS':
            return Response(status_code=200, headers=headers)
