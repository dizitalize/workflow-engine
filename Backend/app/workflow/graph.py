from dataclasses import dataclass, field
from typing import Any
from Backend.app.schemas.node import NodeDefinition, EdgeDefinition


@dataclass
class WorkflowGraph:
    nodes: list[NodeDefinition] = field(default_factory=list)
    edges: list[EdgeDefinition] = field(default_factory=list)
    _node_map: dict[str, NodeDefinition] = field(default_factory=dict, init=False)
    _adjacency: dict[str, list[EdgeDefinition]] = field(default_factory=dict, init=False)
    _reverse_adjacency: dict[str, list[EdgeDefinition]] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self._build_indices()

    def _build_indices(self):
        self._node_map = {node.id: node for node in self.nodes}
        self._adjacency = {}
        self._reverse_adjacency = {}

        for edge in self.edges:
            if edge.source not in self._adjacency:
                self._adjacency[edge.source] = []
            self._adjacency[edge.source].append(edge)

            if edge.target not in self._reverse_adjacency:
                self._reverse_adjacency[edge.target] = []
            self._reverse_adjacency[edge.target].append(edge)

    def get_node(self, node_id: str) -> NodeDefinition | None:
        return self._node_map.get(node_id)

    def get_next_nodes(self, node_id: str) -> list[NodeDefinition]:
        edges = self._adjacency.get(node_id, [])
        return [self._node_map[edge.target] for edge in edges if edge.target in self._node_map]

    def get_next_edges(self, node_id: str) -> list[EdgeDefinition]:
        return self._adjacency.get(node_id, [])

    def get_previous_nodes(self, node_id: str) -> list[NodeDefinition]:
        edges = self._reverse_adjacency.get(node_id, [])
        return [self._node_map[edge.source] for edge in edges if edge.source in self._node_map]

    def get_incoming_edges(self, node_id: str) -> list[EdgeDefinition]:
        return self._reverse_adjacency.get(node_id, [])

    def get_trigger_nodes(self) -> list[NodeDefinition]:
        return [
            node for node in self.nodes
            if node.type.startswith("trigger.")
        ]

    def get_node_ids(self) -> list[str]:
        return list(self._node_map.keys())

    def has_node(self, node_id: str) -> bool:
        return node_id in self._node_map