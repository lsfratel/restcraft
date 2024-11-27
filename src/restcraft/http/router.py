from __future__ import annotations

import re
from types import MethodType
from typing import Any

from restcraft.exceptions import MethodNotAllowedException, NotFoundException
from restcraft.utils import extract_metadata


class Node:
    def __init__(
        self,
        segment: str = "",
        *,
        param="",
        is_dynamic: bool = False,
    ):
        self.children: dict[str, Node] = {}
        self.patterns: dict[re.Pattern[str], Node] = {}
        self.handlers: dict[str, dict[str, Any]] = {}
        self.segment = segment
        self.param = param
        self.is_dynamic = is_dynamic
        self.view: Any = None


def is_dynamic(segment: str, prefix="<", suffix=">"):
    return segment.startswith(prefix) and segment.endswith(suffix)


class Router:
    def __init__(self, prefix: str = ""):
        self.root: Node = Node()
        self.prefix: str = prefix.rstrip("/")
        self.dynamic_key = ":restcraft:dynamic:"

    def add_route(self, path: str, view: object | type):
        node = self.root
        full_path = f"{self.prefix}{path}"
        segments = self._split_path(full_path)

        for segment in segments:
            if is_dynamic(segment):
                node = node.children.setdefault(self.dynamic_key, Node())
                parts = segment[1:-1].split(":", 1)
                if len(parts) == 2:
                    param, pattern = parts
                else:
                    param, pattern = parts[0], r".*"
                node = node.patterns.setdefault(
                    re.compile(pattern), Node(pattern, param=param, is_dynamic=True)
                )
            else:
                node = node.children.setdefault(segment, Node())

        if node.view is not None:
            raise RuntimeError(
                "Conflicting routes during registration of "
                f"{node.view.__class__.__name__} "
                "and "
                f"{view.__class__.__name__}"
            )

        if type(view) is type:
            view = view()

        node.view = view

        self._register_view_handlers(node, view)

    def dispatch(
        self,
        method: str,
        path: str,
    ) -> tuple[MethodType, dict[str, Any], dict[str, str]]:
        node, params = self._find_node(path)
        if node is None:
            raise NotFoundException

        methods = {method}

        if method == "HEAD":
            methods.add("GET")

        for hmethod in methods:
            if hmethod in node.handlers:
                return (
                    node.handlers[hmethod]["handler"],
                    node.handlers[hmethod]["metadata"],
                    params,
                )

        raise MethodNotAllowedException

    def merge(self, other_router: Router):
        self._merge_nodes(self.root, other_router.root)

    def _find_node(self, path: str):
        node = self.root
        segments = self._split_path(path)
        params: dict[str, str] = {}

        for segment in segments:
            if segment in node.children:
                node = node.children[segment]
            elif self.dynamic_key in node.children:
                dynamic_node = node.children[self.dynamic_key]
                for pattern in dynamic_node.patterns:
                    if match := pattern.match(segment):
                        node = dynamic_node.patterns[pattern]
                        params[node.param] = match.group(0)
                        break

        if node.view is None:
            return None, params

        return node, params

    def _register_view_handlers(self, node: Node, view: object):
        for metadata, handler in extract_metadata(view):
            for verb in metadata["methods"]:
                node.handlers[verb] = {
                    "handler": handler,
                    "metadata": metadata,
                }

    def _merge_nodes(self, node: Node, other: Node):
        if node.view and other.view:
            raise RuntimeError(
                "Conflicting routes during merge of "
                f"{node.view.__class__.__name__} "
                "and "
                f"{other.view.__class__.__name__}"
            )

        node.view = other.view
        node.is_dynamic = other.is_dynamic
        node.param = other.param
        node.segment = other.segment
        node.handlers.update(other.handlers)

        for key, other_child in other.children.items():
            if key in node.children:
                self._merge_nodes(node.children[key], other_child)
            else:
                node.children[key] = other_child

        for key, other_pattern in other.patterns.items():
            if key in node.patterns:
                self._merge_nodes(node.patterns[key], other_pattern)
            else:
                node.patterns[key] = other_pattern

    @classmethod
    def _split_path(cls, path: str) -> list[str]:
        return [part for part in path.split("/") if part]
