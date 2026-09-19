from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    active_version_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkflowVersionBase(BaseModel):
    definition: dict[str, Any]


class WorkflowVersionCreate(WorkflowVersionBase):
    pass


class WorkflowVersionResponse(WorkflowVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_id: str
    version: int
    created_at: datetime


class WorkflowDefinition(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowResponse]
    total: int