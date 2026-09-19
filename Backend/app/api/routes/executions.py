from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from Backend.app.schemas.execution import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionListResponse,
    ExecutionWithNodesResponse,
)
from Backend.app.schemas.workflow import WorkflowDefinition
from Backend.app.services.workflow_service import ExecutionService

router = APIRouter(prefix="/api/v1/executions", tags=["executions"])
execution_service = ExecutionService()


@router.post("/workflows/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(workflow_id: str, data: ExecutionCreate):
    from Backend.app.services.workflow_service import WorkflowVersionService
    from Backend.app.workflow.registry import registry
    
    version_service = WorkflowVersionService()
    version = await version_service.get_active_version(workflow_id)
    
    if not version:
        raise HTTPException(status_code=400, detail="No active version found for workflow")
    
    result = await execution_service.execute_workflow(
        workflow_id,
        version.id,
        version.definition,
        data.input or {}
    )
    
    if result["status"] == "FAILED":
        return ExecutionResponse(
            id=result["execution_id"],
            workflow_id=workflow_id,
            version_id=version.id,
            status=result["status"],
            error=result.get("error"),
        )
    
    return ExecutionResponse(
        id=result["execution_id"],
        workflow_id=workflow_id,
        version_id=version.id,
        status=result["status"],
        output=result.get("output"),
    )


@router.get("", response_model=ExecutionListResponse)
async def list_executions(
    workflow_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    executions, total = await execution_service.list_executions(workflow_id, limit, offset)
    return ExecutionListResponse(
        executions=[ExecutionResponse.model_validate(e) for e in executions],
        total=total,
    )


@router.get("/{execution_id}", response_model=ExecutionWithNodesResponse)
async def get_execution(execution_id: str):
    execution = await execution_service.get_execution_with_nodes(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    node_executions = [
        {
            "id": ne.id,
            "node_id": ne.node_id,
            "node_type": ne.node_type,
            "status": ne.status,
            "input": ne.input,
            "output": ne.output,
            "error": ne.error,
            "retry_count": ne.retry_count,
            "started_at": ne.started_at,
            "finished_at": ne.finished_at,
        }
        for ne in execution.node_executions
    ]
    
    return ExecutionWithNodesResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        version_id=execution.version_id,
        status=execution.status,
        trigger_data=execution.trigger_data,
        output=execution.output,
        error=execution.error,
        started_at=execution.started_at,
        finished_at=execution.finished_at,
        node_executions=node_executions,
    )