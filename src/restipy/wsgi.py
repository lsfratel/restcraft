import types as t

from restipy.core.application import RestiPy


def get_wsgi_application(settings: t.ModuleType):
    app = RestiPy()

    app.bootstrap(settings)

    return app
