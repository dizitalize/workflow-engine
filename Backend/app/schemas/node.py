from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class NodeMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    version: int
    name: str
    description: str
    category: str
    inputs: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []
    config_schema: dict[str, Any] = {}


class NodeDefinition(BaseModel):
    id: str
    type: str
    version: int
    config: dict[str, Any] = {}


class EdgeDefinition(BaseModel):
    source: str
    target: str
    source_handle: Optional[str] = None


class WorkflowDefinition(BaseModel):
    nodes: list[NodeDefinition]
    edges: list[EdgeDefinition]


class ValidationError(BaseModel):
    node_id: str
    code: str
    message: str


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[ValidationError] = []