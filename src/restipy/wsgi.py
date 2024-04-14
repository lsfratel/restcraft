from restipy.core.application import RestiPy


def get_wsgi_application():
    """
    Returns a WSGI application instance.

    Args:
        `settings (ModuleType):` The settings module for the application.

    Returns:
        `RestiPy:` An instance of the RestiPy application.
    """
    app = RestiPy()

    app.bootstrap()

    return app
