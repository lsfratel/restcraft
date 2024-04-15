from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DEBUG = True

MAX_BODY_SIZE = 124 * 1024

VIEWS = {
    'test_app.views.methods_view',
    'test_app.views.test_middlewares_view',
    'test_app.views.test_view',
    'test_app.views.test_multipart_view',
}

MIDDLEWARES = {
    # 'restcraft.middleware.cors.CORSMiddleware',
    'test_app.middlewares.test_middleware',
}

CORS = {
    'origin': ['http://localhost:8000'],
    'headers': ['Content-Type', 'Authorization'],
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'exposed_headers': ['Content-Length', 'X-Foo', 'X-Bar'],
    'credentials': True,
    'max_age': 1200,
}

try:
    from .local_settings import *  # type: ignore # noqa: F403
except ImportError:
    pass
