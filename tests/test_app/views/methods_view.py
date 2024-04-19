from __future__ import annotations

import typing as t

from restcraft.core import JSONResponse, View

if t.TYPE_CHECKING:
    from restcraft.core import Request


class TestHTTPMethodsView(View):
    route = '/'
    methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'HEAD']

    def handler(self, req: Request) -> JSONResponse:
        return JSONResponse({'method': req.method[0]})
