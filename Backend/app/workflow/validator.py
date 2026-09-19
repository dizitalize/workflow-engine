from typing import Any
from Backend.app.schemas.node import NodeDefinition, EdgeDefinition, ValidationError, ValidationResponse
from Backend.app.workflow.graph import WorkflowGraph
from Backend.app.workflow.registry import NodeRegistry


class GraphValidator:
    def __init__(self, registry: NodeRegistry):
        self.registry = registry

    def validate(self, definition: dict[str, Any]) -> ValidationResponse:
        errors: list[ValidationError] = []

        nodes_data = definition.get("nodes", [])
        edges_data = definition.get("edges", [])

        nodes = [NodeDefinition(**n) for n in nodes_data]
        edges = [EdgeDefinition(**e) for e in edges_data]

        graph = WorkflowGraph(nodes=nodes, edges=edges)

        node_ids = [node.id for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            duplicates = [id for id in node_ids if node_ids.count(id) > 1]
            for dup in set(duplicates):
                errors.append(ValidationError(
                    node_id=dup,
                    code="DUPLICATE_NODE_ID",
                    message=f"Duplicate node ID: {dup}"
                ))

        for node in nodes:
            if not self.registry.exists(node.type):
                errors.append(ValidationError(
                    node_id=node.id,
                    code="INVALID_NODE_TYPE",
                    message=f"Unknown node type: {node.type}"
                ))

            node_def = self.registry.get(node.type)
            if node_def:
                config_errors = node_def.validate_config(node.config)
                for err in config_errors:
                    errors.append(ValidationError(
                        node_id=node.id,
                        code="INVALID_CONFIGURATION",
                        message=err
                    ))

        for edge in edges:
            if not graph.has_node(edge.source):
                errors.append(ValidationError(
                    node_id=edge.source,
                    code="MISSING_SOURCE_NODE",
                    message=f"Source node '{edge.source}' does not exist"
                ))
            if not graph.has_node(edge.target):
                errors.append(ValidationError(
                    node_id=edge.target,
                    code="MISSING_TARGET_NODE",
                    message=f"Target node '{edge.target}' does not exist"
                ))

        if not errors:
            cycle_errors = self._detect_cycles(graph)
            errors.extend(cycle_errors)

        if not errors:
            unreachable_errors = self._detect_unreachable_nodes(graph)
            errors.extend(unreachable_errors)

        return ValidationResponse(valid=len(errors) == 0, errors=errors)

    def _detect_cycles(self, graph: WorkflowGraph) -> list[ValidationError]:
        errors: list[ValidationError] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for next_node in graph.get_next_nodes(node_id):
                if next_node.id not in visited:
                    if dfs(next_node.id):
                        return True
                elif next_node.id in rec_stack:
                    errors.append(ValidationError(
                        node_id=next_node.id,
                        code="CYCLE_DETECTED",
                        message=f"Cycle detected involving node: {next_node.id}"
                    ))
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph.get_node_ids():
            if node_id not in visited:
                dfs(node_id)

        return errors

    def _detect_unreachable_nodes(self, graph: WorkflowGraph) -> list[ValidationError]:
        errors: list[ValidationError] = []
        trigger_nodes = graph.get_trigger_nodes()

        if not trigger_nodes:
            return errors

        reachable: set[str] = set()

        def mark_reachable(node_id: str):
            if node_id in reachable:
                return
            reachable.add(node_id)
            for next_node in graph.get_next_nodes(node_id):
                mark_reachable(next_node.id)

        for trigger in trigger_nodes:
            mark_reachable(trigger.id)

        for node in graph.nodes:
            if node.id not in reachable:
                errors.append(ValidationError(
                    node_id=node.id,
                    code="UNREACHABLE_NODE",
                    message=f"Node '{node.id}' is not reachable from any trigger"
                ))

        return errors