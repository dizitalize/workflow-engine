from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ExecutionCreate(BaseModel):
    input: Optional[dict[str, Any]] = None


class NodeExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    node_type: str
    status: str
    input: Optional[dict[str, Any]] = None
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    version_id: str
    status: str
    trigger_data: Optional[dict[str, Any]] = None
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class ExecutionListResponse(BaseModel):
    executions: list[ExecutionResponse]
    total: int


class ExecutionWithNodesResponse(ExecutionResponse):
    node_executions: list[NodeExecutionResponse] = []