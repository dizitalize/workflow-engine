from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass
import json


@dataclass
class NodeMetadata:
    type: str
    version: int
    name: str
    description: str
    category: str
    inputs: list[dict[str, Any]] = None
    outputs: list[dict[str, Any]] = None
    config_schema: dict[str, Any] = None

    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
        if self.config_schema is None:
            self.config_schema = {}


@dataclass
class NodeResult:
    output: Any = None
    error: str | None = None
    success: bool = True


class BaseNode(ABC):
    metadata: NodeMetadata

    @abstractmethod
    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        pass

    @classmethod
    def validate_config(cls, config: dict[str, Any]) -> list[str]:
        errors = []
        schema = cls.metadata.config_schema
        
        if not schema:
            return errors
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in config:
                errors.append(f"Required field '{field}' is missing")
        
        # Check field types
        properties = schema.get("properties", {})
        for field, value in config.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type and not _check_type(value, expected_type):
                    errors.append(f"Field '{field}' must be of type {expected_type}")
        
        return errors


def _check_type(value: Any, expected_type: str) -> bool:
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list,
    }
    expected = type_map.get(expected_type)
    if expected:
        return isinstance(value, expected)
    return True