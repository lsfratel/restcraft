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
    Middleware that handles Cross-Origin Resource Sharing (CORS)..

    This middleware is responsible for configuring the appropriate CORS
    headers in the response based on the settings defined in the application's
    configuration.

    The middleware checks the origin of the incoming request and determines if
    it is allowed based on the configured CORS origins. It then sets the
    appropriate CORS headers in the response, including:
    - Access-Control-Allow-Origin
    - Access-Control-Allow-Methods
    - Access-Control-Allow-Headers
    - Access-Control-Expose-Headers
    - Access-Control-Allow-Credentials
    - Access-Control-Max-Age

    If the origin is not allowed, the middleware returns a 403 Forbidden
    response.

    If the incoming request method is OPTIONS, the middleware returns a 200 OK
    response with the configured CORS headers.
    """

    def __init__(self, app: RestCraft) -> None:
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
        Configures the CORS headers for the specified header key and header
        type.

        Args:
            `header_key (str):` The CORS header key to configure
                (e.g. "Access-Control-Allow-Origin").
            `header_type (str):` The name of the attribute on the
                CORSMiddleware instance that contains the header value
                (e.g. "origins").

        Returns:
            `dict[str, str]:` A dictionary containing the configured CORS
                header.
        """
        header_value = getattr(self, header_type, None)
        if not header_value:
            return {}
        if header_value == '*' or '*' in header_value:
            return {header_key: '*'}
        return {header_key: ', '.join(header_value)}

    def configure_credentials(self) -> t.Dict[str, str]:
        """
        Configures the "Access-Control-Allow-Credentials" CORS header based on
        the value of the `credentials`.

        Returns:
            `dict[str, str]:` A dictionary containing the configured
                "Access-Control-Allow-Credentials" CORS header, or an empty
                dictionary if `credentials` is falsy.
        """
        if self.credentials:
            return {'Access-Control-Allow-Credentials': 'true'}
        return {}

    def configure_maxage(self) -> t.Dict[str, str]:
        """
        Configures the "Access-Control-Max-Age" CORS header based on the value
        of the `credentials` attribute.

        Returns:
            `dict[str, str]:` A dictionary containing the configured
                "Access-Control-Max-Age" CORS header, or an empty dictionary
                if `credentials` is falsy.
        """
        if self.credentials is not None:
            return {'Access-Control-Max-Age': str(self.credentials)}
        return {}

    def is_allowed_origin(
        self, origin: str, allowed_origin: t.Union[str, t.List[str]]
    ) -> bool:
        """
        Checks if the given origin is allowed based on the configured allowed
        origins.

        Args:
            `origin (str):` The origin to check.
            `allowed_origin (Union[str, List[str]]):` The allowed origin or
                list of allowed origins.

        Returns:
            `bool:` True if the origin is allowed, False otherwise.
        """
        if isinstance(allowed_origin, str):
            return origin.lower() == allowed_origin.lower()
        return origin.lower() in [ao.lower() for ao in allowed_origin]

    def configure_origin(self, req: Request):
        """
        Configures the "Access-Control-Allow-Origin" CORS header based on the
        configured allowed origins.

        Args:
            `req (Request):` The incoming request.

        Returns:
            `dict[str, str]:` A dictionary containing the configured
                "Access-Control-Allow-Origin" CORS header, or an empty
                dictionary if the origin is not allowed.
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
        Handles CORS (Cross-Origin Resource Sharing) for incoming requests.

        This function is called before a route is executed, and it configures
        the necessary CORS headers based on the configured allowed origins and
        other CORS settings.

        If the origin is not allowed, the function returns a 403 Forbidden
        response. Otherwise, it returns a response with the configured CORS
        headers.

        If the incoming request method is 'OPTIONS', the function returns a
        200 OK response with the configured CORS headers.
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
