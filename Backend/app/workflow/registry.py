from typing import Any
from Backend.app.nodes.base import BaseNode, NodeMetadata


class NodeRegistry:
    def __init__(self):
        self._nodes: dict[str, type[BaseNode]] = {}
        self._metadata: dict[str, NodeMetadata] = {}

    def register(self, node_class: type[BaseNode]) -> None:
        metadata = node_class.metadata
        key = f"{metadata.type}"
        self._nodes[key] = node_class
        self._metadata[key] = metadata

    def get(self, node_type: str) -> type[BaseNode] | None:
        return self._nodes.get(node_type)

    def get_metadata(self, node_type: str) -> NodeMetadata | None:
        return self._metadata.get(node_type)

    def exists(self, node_type: str) -> bool:
        return node_type in self._nodes

    def list(self) -> list[NodeMetadata]:
        return list(self._metadata.values())

    def get_all_types(self) -> list[str]:
        return list(self._nodes.keys())


registry = NodeRegistry()