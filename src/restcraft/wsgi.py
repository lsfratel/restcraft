from restcraft.core.application import RestCraft


def get_wsgi_application() -> RestCraft:
    """
    Returns a RestCraft application instance.

    This function creates a new instance of the RestCraft class, bootstraps it,
    and returns the instance.

    Returns:
        RestCraft: A RestCraft application instance.
    """
    app = RestCraft()

    app.bootstrap()

    return app
