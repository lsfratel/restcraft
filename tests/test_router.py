from restcraft.http import Router
from restcraft.plugin import Plugin
from restcraft.views import metadata


class DummyView:
    @metadata(methods=["GET"])
    def get(self):
        return {"message": "GET response"}


class AnotherDummyView:
    @metadata(methods=["GET"])
    def get(self):
        return {"message": "GET response"}

    @metadata(methods=["PUT"])
    def put(self):
        return {"message": "PUT response"}


def test_router_add_route_find():
    router = Router()
    router.add_route(r"/test", DummyView())

    node, params = router.find("/test")

    assert node is not None
    assert node.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert params == {}


def test_router_dynamic_route():
    router = Router()
    router.add_route(r"/users/<user_id:\d+>", DummyView())
    node, params = router.find("/users/42")
    node2, _ = router.find("/users/asd")

    assert node is not None
    assert node2 is None
    assert node.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert params == {"user_id": "42"}


def test_router_merge_static_and_dynamic_routes():
    router = Router()

    router.add_route("/static", DummyView())
    router.add_route("/dynamic/<id>", AnotherDummyView())

    node_static, params_static = router.find("/static")
    node_dynamic, params_dynamic = router.find("/dynamic/123")

    assert node_static is not None
    assert node_static.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert params_static == {}

    assert node_dynamic is not None
    assert node_dynamic.handlers["PUT"]["handler"]() == {"message": "PUT response"}
    assert params_dynamic == {"id": "123"}


def test_router_merge():
    router1 = Router()
    router2 = Router()

    router1.add_route("/route1", DummyView())
    router2.add_route("/route2/<id>", AnotherDummyView())

    router1.merge(router2)

    node1, _ = router1.find("/route1")
    node2, _ = router1.find("/route2/1")

    assert node1 is not None
    assert node2 is not None

    assert node1.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert node2.handlers["PUT"]["handler"]() == {"message": "PUT response"}


def test_router_cache_plugin():
    class TestPlugin(Plugin):
        name = "test_plugin"

        def apply(self, callback, metadata):  # type: ignore
            def wrapper(*args, **kwargs):
                return {"plugin_applied": callback()}

            return wrapper

    router = Router()
    router.add_route("/test", DummyView())

    plugin = TestPlugin()
    router.cache_plugin(plugin)

    node, _ = router.find("/test")
    assert node is not None
    assert node.handlers["GET"]["handler"]() == {
        "plugin_applied": {"message": "GET response"}
    }


def test_router_not_found():
    router = Router()

    node, params = router.find("/nonexistent")

    assert node is None
    assert params is None


def test_router_method_not_allowed():
    router = Router()

    router.add_route("/test", AnotherDummyView())

    node, _ = router.find("/test")

    assert node is not None
    assert "POST" not in node.handlers  # Ensure POST is not added
    assert "GET" in node.handlers  # Ensure GET is added


def test_router_conflicting_routes():
    router = Router()

    router.add_route("/test", DummyView())
    try:
        router.add_route("/test", AnotherDummyView())
    except ValueError as e:
        assert str(e) == "Conflicting views found during merge"


def test_router_plugin_with_restriction():
    class TestPlugin(Plugin):
        name = "test_plugin"

        def apply(self, callback, metadata):  # type: ignore
            def wrapper(*args, **kwargs):
                return {"plugin_applied": callback()}

            return wrapper

    class DummyView2:
        @metadata(methods=["GET"], plugins=["-test_plugin"])
        def get(self):
            return {"message": "GET response"}

    router = Router()
    plugin = TestPlugin()
    view = DummyView2()

    router.add_route("/test", view)

    router.cache_plugin(plugin)

    node, _ = router.find("/test")
    assert node is not None
    assert node.handlers["GET"]["handler"]() == {"message": "GET response"}


def test_router_plugin_with_include():
    class TestPlugin(Plugin):
        name = "test_plugin"

        def apply(self, callback, metadata):  # type: ignore
            def wrapper(*args, **kwargs):
                return {"plugin_applied": callback()}

            return wrapper

    class DummyView2:
        @metadata(methods=["GET"], plugins=["test_plugin"])
        def get(self):
            return {"message": "GET response"}

    router = Router()
    view = DummyView2()

    router.add_route("/test", view)

    plugin = TestPlugin()
    router.cache_plugin(plugin)

    node, _ = router.find("/test")
    assert node is not None
    assert node.handlers["GET"]["handler"]() == {
        "plugin_applied": {"message": "GET response"}
    }


def test_router_auto_generate_head_handler():
    router = Router()
    router.add_route("/head_test", DummyView())
    node, _ = router.find("/head_test")

    assert node is not None
    assert "HEAD" in node.handlers
    assert node.handlers["HEAD"]["handler"]() == {"message": "GET response"}


def test_router_auto_generate_options_handler():
    router = Router()

    router.add_route("/options_test", DummyView())
    node, _ = router.find("/options_test")

    assert node is not None
    assert "OPTIONS" in node.handlers
    response = node.handlers["OPTIONS"]["handler"]()
    assert response.status == "204 No Content"


def test_router_custom_head_and_options():
    class CustomView:
        @metadata(methods=["GET", "HEAD", "OPTIONS"])
        def get(self):
            return {"message": "Custom GET response"}

    router = Router()

    router.add_route("/custom", CustomView())
    node, _ = router.find("/custom")

    assert node is not None
    assert node.handlers["HEAD"]["handler"]() == {"message": "Custom GET response"}
    assert node.handlers["OPTIONS"]["handler"]() == {"message": "Custom GET response"}


def test_router_conflicting_dynamic_routes():
    router = Router()

    router.add_route("/test/<id>", DummyView())
    try:
        router.add_route("/test/<name>", AnotherDummyView())
    except ValueError as e:
        assert str(e) == "Conflicting views found during merge"


def test_router_auto_generate_head_and_options_metadata():
    router = Router()
    router.add_route("/test", DummyView())
    node, _ = router.find("/test")

    assert node is not None
    assert "HEAD" in node.handlers
    assert "OPTIONS" in node.handlers

    head_metadata = node.handlers["HEAD"]["metadata"]
    get_metadata = node.handlers["GET"]["metadata"]

    options_metadata = node.handlers["OPTIONS"]["metadata"]
    methods = list(node.handlers.keys())

    assert head_metadata == {**get_metadata, "methods": ["GET", "HEAD"]}
    assert options_metadata == {"methods": methods, "plugins": ["..."]}


def test_router_head_and_options_isolation():
    router = Router()
    router.add_route("/test", DummyView())

    node, _ = router.find("/test")
    assert node is not None

    head_handler = node.handlers["HEAD"]["handler"]
    options_handler = node.handlers["OPTIONS"]["handler"]

    assert head_handler is node.handlers["GET"]["handler"]
    assert options_handler == router._handler_options


def test_router_dynamic_route_with_head_and_options():
    router = Router()
    router.add_route("/users/<user_id>", DummyView())
    node, _ = router.find("/users/42")

    assert node is not None
    assert "HEAD" in node.handlers
    assert "OPTIONS" in node.handlers
    assert node.handlers["HEAD"]["handler"]() == {"message": "GET response"}
    response = node.handlers["OPTIONS"]["handler"]()
    assert response.status == "204 No Content"
