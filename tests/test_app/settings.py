DEBUG = True

MAX_BODY_SIZE = 124 * 1024

VIEWS = {
    'test_app.views.methods_view',
    'test_app.views.test_middlewares_view',
    'test_app.views.test_view',
    'test_app.views.test_multipart_view',
}

MIDDLEWARES = {
    'test_app.middlewares.test_middleware',
}

try:
    from test_app.local_settings import *  # type: ignore # noqa: F403
except ImportError:
    pass
