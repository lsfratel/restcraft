from restcraft.contrib.plugins.cors import CORSPlugin
from restcraft.http.request import Request
from restcraft.http.response import Response


def test_cors_plugin():
    environ = {
        "REQUEST_METHOD": "OPTIONS",
        "HTTP_ORIGIN": "http://example.com",
        "PATH_INFO": "/test",
    }

    Request.bind(environ)

    plugin = CORSPlugin(allow_origins=["http://example.com"])
    response = plugin.apply(lambda: Response(status=200), metadata={})()

    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert response.status == "204 No Content"
    Request.clear()
