import unittest

from restcraft.core.exceptions import HTTPException
from restcraft.core.routing.manager import RouteManager
from restcraft.core.routing.view import View


class GenericView(View):
    def __init__(self, route: str, methods: list[str], name: str) -> None:
        self.route = route
        self.methods = methods
        self.name = name


class TestRouter(unittest.TestCase):
    routes = [
        {
            'home': '/|GET',
            'users': '/users|GET',
            'users_create': '/users|POST',
            'users_id': '/users/<id:int>|GET',
            'users_id_update': '/users/<id:int>|PUT',
            'users_id_delete': '/users/<id:int>|DELETE',
            'users_id_posts': '/users/<id:int>/posts|GET',
            'users_id_posts_create': '/users/<id:int>/posts|POST',
            'product_optional': '/product/<?id:int>|GET',
            'product_uuid': '/product/<id:uuid>|GET',
            'cart_slug': '/cart/<id:slug>|GET',
            'multiple_ids': '/multiple/<id:int>/<id2:str>|GET',
            'multiple_optional_ids': '/multiple-2/<id:int>/<?optio:int>|GET',
            'nested_optional_ids': '/nested/<?id:int>/<id2:int>|GET',
        }
    ]

    @classmethod
    def setUpClass(cls) -> None:
        cls.router = RouteManager()
        for route in cls.routes:
            for name, route_str in route.items():
                route_str, methods = route_str.split('|')
                methods = methods.split(',')
                view = GenericView(route_str, methods, name)
                cls.router.add_route(view)

    def test_router_home(self):
        route, params = self.router.resolve('GET', '/')
        self.assertEqual(getattr(route.view, 'name'), 'home')
        self.assertEqual(params, {})

    def test_router_users(self):
        route, params = self.router.resolve('GET', '/users')
        self.assertEqual(getattr(route.view, 'name'), 'users')
        self.assertEqual(params, {})

    def test_router_users_create(self):
        route, params = self.router.resolve('POST', '/users')
        self.assertEqual(getattr(route.view, 'name'), 'users_create')
        self.assertEqual(params, {})

    def test_router_users_id(self):
        route, params = self.router.resolve('GET', '/users/1')
        self.assertEqual(getattr(route.view, 'name'), 'users_id')
        self.assertEqual(params, {'id': 1})

    def test_router_users_id_update(self):
        route, params = self.router.resolve('PUT', '/users/1')
        self.assertEqual(getattr(route.view, 'name'), 'users_id_update')
        self.assertEqual(params, {'id': 1})

    def test_router_users_id_delete(self):
        route, params = self.router.resolve('DELETE', '/users/1')
        self.assertEqual(getattr(route.view, 'name'), 'users_id_delete')
        self.assertEqual(params, {'id': 1})

    def test_router_users_id_posts(self):
        route, params = self.router.resolve('GET', '/users/1/posts')
        self.assertEqual(getattr(route.view, 'name'), 'users_id_posts')
        self.assertEqual(params, {'id': 1})

    def test_router_users_id_posts_create(self):
        route, params = self.router.resolve('POST', '/users/1/posts')
        self.assertEqual(getattr(route.view, 'name'), 'users_id_posts_create')
        self.assertEqual(params, {'id': 1})

    def test_router_product_optional(self):
        route, params = self.router.resolve('GET', '/product')
        self.assertEqual(getattr(route.view, 'name'), 'product_optional')
        self.assertEqual(params, {'id': None})

        route, params = self.router.resolve('GET', '/product/1')
        self.assertEqual(getattr(route.view, 'name'), 'product_optional')
        self.assertEqual(params, {'id': 1})

    def test_router_product_uuid(self):
        route, params = self.router.resolve(
            'GET', '/product/12345678-1234-5678-1234-567812345678'
        )
        self.assertEqual(getattr(route.view, 'name'), 'product_uuid')
        self.assertEqual(
            params, {'id': '12345678-1234-5678-1234-567812345678'}
        )

    def test_router_cart_slug(self):
        route, params = self.router.resolve('GET', '/cart/my-cart')
        self.assertEqual(getattr(route.view, 'name'), 'cart_slug')
        self.assertEqual(params, {'id': 'my-cart'})

    def test_router_multiple_ids(self):
        route, params = self.router.resolve('GET', '/multiple/1/abc')
        self.assertEqual(getattr(route.view, 'name'), 'multiple_ids')
        self.assertEqual(params, {'id': 1, 'id2': 'abc'})

    def test_router_multiple_optional_ids(self):
        route, params = self.router.resolve('GET', '/multiple-2/1')
        self.assertEqual(getattr(route.view, 'name'), 'multiple_optional_ids')
        self.assertEqual(params, {'id': 1, 'optio': None})

        route, params = self.router.resolve('GET', '/multiple-2/1/2')
        self.assertEqual(getattr(route.view, 'name'), 'multiple_optional_ids')
        self.assertEqual(params, {'id': 1, 'optio': 2})

    def test_router_nested_optional_ids(self):
        route, params = self.router.resolve('GET', '/nested/1')
        self.assertEqual(getattr(route.view, 'name'), 'nested_optional_ids')
        self.assertEqual(params, {'id': None, 'id2': 1})

        route, params = self.router.resolve('GET', '/nested/1/2')
        self.assertEqual(getattr(route.view, 'name'), 'nested_optional_ids')
        self.assertEqual(params, {'id': 1, 'id2': 2})

    def test_router_types(self):
        with self.assertRaises(HTTPException):
            _ = self.router.resolve('GET', '/nested/a')
