from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class ExecutionContext:
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    workflow_id: str = ""
    workflow_version_id: str = ""
    trigger_data: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    node_results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    current_node_id: str = ""
    cancelled: bool = False

    def get_node_result(self, node_id: str) -> Any:
        return self.node_results.get(node_id)

    def set_node_result(self, node_id: str, result: Any) -> None:
        self.node_results[node_id] = result

    def set_variable(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def check_cancellation(self) -> None:
        if self.cancelled:
            raise ExecutionCancelledError(f"Execution {self.execution_id} was cancelled")

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_version_id": self.workflow_version_id,
            "trigger_data": self.trigger_data,
            "variables": self.variables,
            "node_results": self.node_results,
            "metadata": self.metadata,
            "current_node_id": self.current_node_id,
            "cancelled": self.cancelled,
        }


class ExecutionCancelledError(Exception):
    pass