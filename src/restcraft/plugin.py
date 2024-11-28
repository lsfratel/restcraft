from __future__ import annotations

from typing import TYPE_CHECKING

from restcraft.http import Response

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from restcraft.restcraft import RestCraft


class PluginException(Exception): ...


class Plugin:
    """Base class for all plugins.

    This class provides a default implementation for plugin methods.
    Plugins can extend this class and override the methods as needed.
    """

    name: str

    def setup(self, manager: PluginManager):
        """Sets up the plugin with the given manager.

        This method is called when the plugin is registered. It checks
        if a plugin of the same type is already installed.

        Args:
            manager (PluginManager): The manager responsible for plugin lifecycle.

        Raises:
            PluginException: If the plugin is already installed.
        """
        if any(isinstance(plugin, self.__class__) for plugin in manager.plugins):
            raise PluginException(f"Plugin {self.name} already installed.")

    def before_route(
        self, dispatcher: Callable[..., tuple]
    ) -> Callable[..., tuple] | Response:
        """Modifies or wraps the route dispatcher.

        This method is called before the application's route is dispatched.

        Args:
            dispatcher (Callable[..., tuple]): The route dispatcher.

        Returns:
            Callable[..., tuple] | Response: The modified route dispatcher
            or a Response object if the plugin wants to short-circuit the request.
        """
        return dispatcher

    def before_handler(
        self, handler: Callable[..., Response], metadata: dict[str, Any]
    ) -> Callable[..., Response] | Response:
        """Modifies or wraps the handler function.

        This method is called before the application's route handler is executed.

        Args:
            handler (Callable[..., Response]): The handler function.
            metadata (dict[str, Any]): The route metadata.

        Returns:
            Callable[..., Response] | Response: The modified handler function
            or a Response object if the plugin wants to short-circuit the request.
        """
        return handler

    def close(self):
        """Performs cleanup tasks for the plugin.

        This method is called when the plugin is unregistered.
        Override this method to release any resources held by the plugin.
        """
        pass


class PluginManager:
    """Manages the lifecycle of plugins.

    A plugin manager is responsible for instantiating plugins, calling
    their setup methods, and keeping track of the plugins that are
    registered with the application.
    """

    def __init__(self, app: RestCraft):
        """Initializes the plugin manager.

        Args:
            app (RestCraft): The application that the plugins are being
                registered with.
        """
        self.app = app
        self.plugins: list[Plugin] = []

    def register(self, plugin: Plugin):
        """Registers a new plugin with the application.

        The plugin is instantiated and its setup method is called.

        Args:
            plugin (Plugin): The plugin to register.
        """

        plugin.setup(self)
        self.plugins.append(plugin)

    def unregister(self, plugin: Plugin | str):
        """Unregisters a plugin from the application.

        The plugin is removed from the list of registered plugins and
        its close method is called.

        Args:
            plugin (Plugin | str): The plugin to unregister. If a string
                is provided, it is used to look up the plugin in the list
                of registered plugins.
        """

        if isinstance(plugin, Plugin):
            plugin.close()
            self.plugins.remove(plugin)

        p = next((p for p in self.plugins if p.name == plugin), None)

        if p is not None:
            p.close()
            self.plugins.remove(p)

    def before_route(
        self, dispatcher: Callable[..., tuple]
    ) -> Callable[..., tuple] | Response:
        """Calls the before_route method of each plugin.

        This method is called before the application's route is
        dispatched. It allows plugins to modify or wrap the route
        dispatcher.

        Args:
            dispatcher (Callable[..., tuple]): The route dispatcher.

        Returns:
            Callable[..., tuple] | Response: The modified route
                dispatcher, or a Response object if the plugin wants
                to short-circuit the request.
        """

        _dispatcher = dispatcher
        for plugin in self.plugins:
            _dispatcher = plugin.before_route(dispatcher)
            if isinstance(_dispatcher, Response):
                return _dispatcher

        return _dispatcher

    def before_handler(
        self, handler: Callable[..., Response], metadata: dict[str, Any]
    ) -> Callable[..., Response] | Response:
        """Calls the before_handler method of each plugin.

        This method is called before the application's route is
        dispatched. It allows plugins to modify or wrap the handler
        function that is responsible for generating the response.

        Args:
            handler (Callable[..., Response]): The handler function.
            metadata (dict[str, Any]): The route metadata.

        Returns:
            Callable[..., Response] | Response: The modified handler
                function, or a Response object if the plugin wants
                to short-circuit the request.
        """

        _handler = handler
        _allowed = metadata.get("plugins", [])
        for plugin in self.plugins:
            if f"-{plugin.name}" in _allowed or (
                "..." not in _allowed and plugin.name not in _allowed
            ):
                continue

            _handler = plugin.before_handler(_handler, metadata)
            if isinstance(_handler, Response):
                return _handler

        return _handler
