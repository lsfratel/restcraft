from __future__ import annotations

import re
from collections.abc import Callable
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
    """A router for handling HTTP requests."""

    def __init__(self, prefix: str = ""):
        self.root: Node = Node()
        self.prefix: str = prefix.rstrip("/")
        self.dynamic_key = ":restcraft:dynamic:"
        self.handlers = []

    def add_route(self, path: str, view: object | type):
        """Registers a route for a given path and view.

        Args:
            path: The path to register. This path may contain dynamic segments.
            view: The view object or class to register.

        Raises:
            RuntimeError: If a conflicting route is detected.
        """
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
    ) -> tuple[Callable, dict[str, Any], dict[str, str]]:
        """Finds the view handler for a given method and path.

        Args:
            method: The HTTP method.
            path: The path to find the view for.

        Returns:
            A tuple containing the view handler, the metadata associated with the
                view, and the parameters extracted from the path.

        Raises:
            NotFoundException: If a matching route is not found.
            MethodNotAllowedException: If the method is not supported by the
                matched route.
        """

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
        """Merges the routes of another router into this one.

        This method merges the routes of `other_router` into this router. It
        recursively traverses the nodes of both routers and merges them based on
        their paths. If a node with the same path already exists in this router,
        it will be replaced by the node from `other_router`.

        Args:
            other_router: The router whose routes should be merged into this one.
        """

        self._merge_nodes(self.root, other_router.root)

    def _find_node(self, path: str):
        """Finds a node in the router tree by path.

        This method traverses the router tree based on the given path and
        returns the corresponding node and any matched URL parameters.

        Args:
            path: The path to find the node for.

        Returns:
            A tuple of the node and a dictionary of any matched URL parameters.
            If the path is not found, the node is None.
        """

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
        """Registers all view handlers in the given node.

        This method iterates over all extracted metadata and handlers from the given
        view object and registers them in the given node. It also keeps track of all
        registered handlers in the `handlers` list.

        Args:
            node (Node): The node to register the handlers in.
            view (object): The view object to extract handlers and metadata from.
        """

        for metadata, handler in extract_metadata(view):
            for verb in metadata["methods"]:
                self.handlers.append(handler)
                node.handlers[verb] = {
                    "handler": handler,
                    "metadata": metadata,
                }

    def _merge_nodes(self, node: Node, other: Node):
        """Merges two nodes in the router tree.

        This method recursively merges the two nodes. If a node with the same
        path already exists in the first node, it will be replaced by the
        corresponding node from the second node.

        Raises:
            RuntimeError: If a node with the same path already exists in the
                first node and has a view registered.
        """

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
        """Splits a path into a list of parts.

        This function splits a path into a list of strings, ignoring empty
        parts. This is used to split the path part of a URL into the
        individual parts that are compared against the router tree.

        Args:
            path: The path to split.

        Returns:
            A list of strings, where each string is a part of the path.
        """

        return [part for part in path.split("/") if part]
