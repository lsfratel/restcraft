from __future__ import annotations

from functools import lru_cache
from types import MethodType
from typing import Any

from restcraft.http.response import Response
from restcraft.plugin import Plugin
from restcraft.utils import extract_metadata


class Node:
    def __init__(
        self,
        part: str = "",
        is_dynamic: bool = False,
        handlers: dict[str, dict[str, Any]] | None = None,
        view: object | None = None,
    ):
        self.part = part
        self.is_dynamic = is_dynamic
        self.handlers = handlers or {}
        self.children: dict[str, Node] = {}
        self.view = view

    def merge(self, other_node: Node):
        if self.view and other_node.view:
            raise ValueError("Conflicting views found during merge")
        self.view = self.view or other_node.view
        self.is_dynamic = self.is_dynamic or other_node.is_dynamic
        self.handlers.update(other_node.handlers)

    def add_child(self, key: str, part: str, is_dynamic: bool) -> Node:
        if key not in self.children:
            self.children[key] = Node(part, is_dynamic)
        return self.children[key]


class Router:
    def __init__(self, prefix: str = ""):
        self.root: Node = Node()
        self.prefix: str = prefix.rstrip("/")

    def add_route(self, path: str, view: object | type):
        full_path = f"{self.prefix}{path}"
        parts = self._split_path(full_path)
        current_node = self.root

        for part in parts:
            is_dynamic = part.startswith(":")
            key = ":" if is_dynamic else part
            current_node = current_node.add_child(key, part, is_dynamic)

        if type(view) is type:
            view = view()

        self._register_view_handlers(current_node, view)
        self._setup_head_handler(current_node)
        self._setup_options_handler(current_node)

    def _setup_head_handler(self, node: Node):
        if "HEAD" in node.handlers or "GET" not in node.handlers:
            return

        handler = node.handlers["GET"]["handler"]
        metadata = node.handlers["GET"]["metadata"]
        metadata["methods"].append("HEAD")

        if "OPTIONS" not in metadata["methods"]:
            metadata["methods"].append("OPTIONS")

        node.handlers["HEAD"] = {
            "handler": handler,
            "metadata": metadata,
        }

    def _setup_options_handler(self, node: Node):
        if "OPTIONS" in node.handlers:
            return

        methods = list(node.handlers.keys())
        methods.append("OPTIONS")

        node.handlers["OPTIONS"] = {
            "handler": self._handler_options,
            "metadata": {
                "methods": methods,
                "plugins": ["..."],
            },
        }

    def merge(self, other_router: Router):
        self._merge_nodes(self.root, other_router.root)
        self.find.cache_clear()

    def cache_plugin(self, plugin: Plugin):
        self._cache_plugins(self.root, plugin)

    @lru_cache(maxsize=256)
    def find(self, path: str) -> tuple[Node | None, dict[str, str] | None]:
        parts = self._split_path(path)
        current_node = self.root
        params = {}

        for part in parts:
            current_node = self._match_part(current_node, part, params)
            if not current_node:
                return None, None

        return (current_node, params) if current_node.view else (None, None)

    def _match_part(self, node: Node, part: str, params: dict):
        if part in node.children:
            return node.children[part]

        if ":" in node.children:
            dynamic_node = node.children[":"]
            params[dynamic_node.part[1:]] = part
            return dynamic_node

        return None

    def _register_view_handlers(self, node: Node, view: object):
        for verb, meta in extract_metadata(view):
            for method_name, method_meta in meta.items():
                node.handlers[verb] = {
                    "handler": getattr(view, method_name),
                    "metadata": method_meta,
                }
        node.view = view

    def _merge_nodes(self, current_node: Node, other_node: Node):
        current_node.merge(other_node)
        for key, other_child in other_node.children.items():
            if key in current_node.children:
                self._merge_nodes(current_node.children[key], other_child)
            else:
                current_node.children[key] = other_child

    def _cache_plugins(self, node: Node, plugin: Plugin):
        stack = [node]
        while stack:
            current_node = stack.pop()
            for child in current_node.children.values():
                stack.append(child)

            if not current_node.view:
                continue

            for verb, options in current_node.handlers.items():
                metadata = options["metadata"]
                allowed = set(metadata["plugins"])
                if f"-{plugin.name}" in allowed:
                    continue
                cached_plugins = self._cached_plugins(options["handler"])
                if (
                    "..." in allowed or plugin.name in allowed
                ) and f"{verb}_{plugin.name}" not in cached_plugins:
                    options["handler"] = plugin.apply(
                        options["handler"], options["metadata"]
                    )
                    cached_plugins.add(f"{verb}_{plugin.name}")

    @staticmethod
    def _cached_plugins(handler: MethodType) -> set:
        return getattr(
            handler.__func__,
            "__cached__",
            setattr(handler.__func__, "__cached__", set())
            or handler.__func__.__cached__,  # type: ignore
        )

    @staticmethod
    def _split_path(path: str) -> list[str]:
        """Split the path into its components."""
        return [part for part in path.split("/") if part]

    def _handler_options(self, *args, **kwargs):
        return Response(status=204)
