from restcraft.core.application import RestCraft


def get_wsgi_application() -> RestCraft:
    """
    Returns a WSGI application instance.

    Args:
        `settings (ModuleType):` The settings module for the application.

    Returns:
        `RestCraft:` An instance of the RestCraft application.
    """
    app = RestCraft()

    app.bootstrap()

    return app
