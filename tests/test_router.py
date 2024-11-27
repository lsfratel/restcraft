import pytest

from restcraft.http import Router
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

    node, params = router._find_node("/test")

    assert node is not None
    assert node.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert params == {}


def test_router_dynamic_route():
    router = Router()
    router.add_route(r"/users/<user_id:\d+>", DummyView())

    node, params = router._find_node("/users/42")
    node2, _ = router._find_node("/users/asd")

    assert node is not None
    assert node2 is None
    assert node.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert params == {"user_id": "42"}


def test_router_merge_static_and_dynamic_routes():
    router = Router()

    router.add_route("/static", DummyView())
    router.add_route("/dynamic/<id>", AnotherDummyView())

    node_static, params_static = router._find_node("/static")
    node_dynamic, params_dynamic = router._find_node("/dynamic/123")

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

    node1, _ = router1._find_node("/route1")
    node2, _ = router1._find_node("/route2/1")

    assert node1 is not None
    assert node2 is not None

    assert node1.handlers["GET"]["handler"]() == {"message": "GET response"}
    assert node2.handlers["PUT"]["handler"]() == {"message": "PUT response"}


def test_router_merge_conflict():
    router1 = Router()
    router2 = Router()

    router1.add_route("/route1", DummyView())
    router2.add_route("/route1", AnotherDummyView())

    with pytest.raises(RuntimeError) as e:
        router1.merge(router2)
        assert (
            str(e.value)
            == "Conflicting routes during merge of DummyView and AnotherDummyView"
        )


def test_router_not_found():
    router = Router()

    node, params = router._find_node("/nonexistent")

    assert node is None
    assert params == {}


def test_router_method_not_allowed():
    router = Router()

    router.add_route("/test", AnotherDummyView())

    node, _ = router._find_node("/test")

    assert node is not None
    assert "POST" not in node.handlers  # Ensure POST is not added
    assert "GET" in node.handlers  # Ensure GET is added


def test_router_conflicting_routes():
    router = Router()

    router.add_route("/test", DummyView())
    with pytest.raises(RuntimeError) as e:
        router.add_route("/test", AnotherDummyView())
        assert (
            str(e.value)
            == "Conflicting routes during registration of DummyView and AnotherDummyView"
        )


def test_router_conflicting_dynamic_routes():
    router = Router()

    router.add_route("/test/<id>", DummyView())
    with pytest.raises(RuntimeError) as e:
        router.add_route("/test/<name>", AnotherDummyView())
        assert (
            str(e.value)
            == "Conflicting routes during registration of DummyView and AnotherDummyView"
        )


def test_router_head_as_get():
    router = Router()
    router.add_route("/head_test", DummyView())
    handler, metadata, params = router.dispatch("HEAD", "/head_test")

    assert handler() == {"message": "GET response"}
    assert params == {}
    assert metadata == {"methods": ["GET"], "plugins": ["..."]}


def test_router_custom_head_and_options():
    class CustomView:
        @metadata(methods=["GET", "HEAD", "OPTIONS"])
        def get(self):
            return {"message": "Custom GET response"}

    router = Router()

    router.add_route("/custom", CustomView())
    node, _ = router._find_node("/custom")

    assert node is not None
    assert node.handlers["HEAD"]["handler"]() == {"message": "Custom GET response"}
    assert node.handlers["OPTIONS"]["handler"]() == {"message": "Custom GET response"}
