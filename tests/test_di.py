import unittest

from restcraft.core.di.container import DependencyManager, inject


class FakeDependency:
    def __init__(self):
        self.value = 'dependency_value'


class TestDependencyManager(unittest.TestCase):
    def test_singleton_instance(self):
        manager1 = DependencyManager.instance()
        manager2 = DependencyManager.instance()
        self.assertIs(manager1, manager2)

    def test_dependency_registration_and_resolution(self):
        manager = DependencyManager.instance()
        manager.register(FakeDependency, 'singleton')
        dep = manager.resolve('FakeDependency')
        self.assertIsInstance(dep, FakeDependency)

    def test_invalid_scope_registration(self):
        manager = DependencyManager.instance()
        with self.assertRaises(ValueError):
            manager.register(FakeDependency, 'invalid_scope')

    def test_singleton_behavior(self):
        manager = DependencyManager.instance()
        dep1 = manager.resolve('FakeDependency')
        dep2 = manager.resolve('FakeDependency')
        self.assertIs(dep1, dep2)

    def test_transient_behavior(self):
        manager = DependencyManager.instance()
        manager.register(FakeDependency, 'transient')
        dep1 = manager.resolve('FakeDependency')
        dep2 = manager.resolve('FakeDependency')
        self.assertIsNot(dep1, dep2)

    def test_scoped_behavior(self):
        manager = DependencyManager.instance()
        manager.register(FakeDependency, 'scoped')
        dep1 = manager.resolve('FakeDependency')
        dep2 = manager.resolve('FakeDependency')
        self.assertIs(dep1, dep2)

        manager.clear_scoped()
        dep3 = manager.resolve('FakeDependency')
        self.assertIsNot(dep1, dep3)

    def test_inject_decorator(self):
        manager = DependencyManager.instance()
        manager.register(FakeDependency, 'singleton')

        @inject
        def function_to_inject(fake_dep: FakeDependency):
            return fake_dep.value

        result = function_to_inject()
        self.assertEqual(result, 'dependency_value')
