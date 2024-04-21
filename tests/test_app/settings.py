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
    'test_app.middlewares.test_middleware',
}

SERVICES = {
    'transient': [
        'test_app.services.transient.MyTransientService',
    ],
}


try:
    from .local_settings import *  # type: ignore reportMissingImports  # noqa: F403
except ImportError:
    pass
