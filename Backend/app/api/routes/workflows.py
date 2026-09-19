from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from Backend.app.schemas.workflow import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowResponse,
    WorkflowListResponse,
    WorkflowVersionCreate,
    WorkflowVersionResponse,
    WorkflowDefinition,
)
from Backend.app.schemas.node import ValidationResponse
from Backend.app.services.workflow_service import WorkflowService, WorkflowVersionService
from Backend.app.workflow.registry import registry

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])
workflow_service = WorkflowService()
version_service = WorkflowVersionService()


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(data: WorkflowCreate):
    workflow = await workflow_service.create_workflow(data.name, data.description)
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    workflows, total = await workflow_service.list_workflows(limit, offset)
    return WorkflowListResponse(
        workflows=[WorkflowResponse.model_validate(w) for w in workflows],
        total=total,
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    workflow = await workflow_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, data: WorkflowUpdate):
    workflow = await workflow_service.update_workflow(workflow_id, data.name, data.description)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(workflow)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str):
    deleted = await workflow_service.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/{workflow_id}/validate", response_model=ValidationResponse)
async def validate_workflow(workflow_id: str, definition: WorkflowDefinition):
    result = await workflow_service.validate_workflow(workflow_id, definition.model_dump())
    return result


@router.post("/{workflow_id}/versions", response_model=WorkflowVersionResponse, status_code=201)
async def create_version(workflow_id: str, data: WorkflowVersionCreate):
    version = await version_service.create_version(workflow_id, data.definition)
    return WorkflowVersionResponse.model_validate(version)


@router.get("/{workflow_id}/versions", response_model=list[WorkflowVersionResponse])
async def list_versions(workflow_id: str):
    versions = await version_service.list_versions(workflow_id)
    return [WorkflowVersionResponse.model_validate(v) for v in versions]


@router.get("/{workflow_id}/versions/active", response_model=WorkflowVersionResponse)
async def get_active_version(workflow_id: str):
    version = await version_service.get_active_version(workflow_id)
    if not version:
        raise HTTPException(status_code=404, detail="No active version found")
    return WorkflowVersionResponse.model_validate(version)


@router.put("/{workflow_id}/versions/{version_id}/activate", response_model=WorkflowResponse)
async def activate_version(workflow_id: str, version_id: str):
    workflow = await version_service.set_active_version(workflow_id, version_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow or version not found")
    return WorkflowResponse.model_validate(workflow)