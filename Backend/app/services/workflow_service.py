from typing import Optional
from Backend.app.db.database import get_session
from Backend.app.repositories.workflow_repo import WorkflowRepository, WorkflowVersionRepository, ExecutionRepository
from Backend.app.workflow.validator import GraphValidator
from Backend.app.workflow.registry import registry
from Backend.app.workflow.engine import execute_workflow


class WorkflowService:
    def __init__(self):
        self.validator = GraphValidator(registry)

    async def create_workflow(self, name: str, description: Optional[str] = None):
        async with get_session() as session:
            repo = WorkflowRepository(session)
            return await repo.create(name, description)

    async def get_workflow(self, workflow_id: str):
        async with get_session() as session:
            repo = WorkflowRepository(session)
            return await repo.get(workflow_id)

    async def list_workflows(self, limit: int = 50, offset: int = 0):
        async with get_session() as session:
            repo = WorkflowRepository(session)
            workflows = await repo.list(limit, offset)
            total = await repo.count()
            return workflows, total

    async def update_workflow(self, workflow_id: str, name: Optional[str] = None, description: Optional[str] = None):
        async with get_session() as session:
            repo = WorkflowRepository(session)
            return await repo.update(workflow_id, name, description)

    async def delete_workflow(self, workflow_id: str) -> bool:
        async with get_session() as session:
            repo = WorkflowRepository(session)
            return await repo.delete(workflow_id)

    async def validate_workflow(self, workflow_id: str, definition: dict):
        return self.validator.validate(definition)


class WorkflowVersionService:
    async def create_version(self, workflow_id: str, definition: dict):
        async with get_session() as session:
            repo = WorkflowVersionRepository(session)
            return await repo.create(workflow_id, definition)

    async def get_version(self, version_id: str):
        async with get_session() as session:
            repo = WorkflowVersionRepository(session)
            return await repo.get(version_id)

    async def list_versions(self, workflow_id: str):
        async with get_session() as session:
            repo = WorkflowVersionRepository(session)
            return await repo.list_by_workflow(workflow_id)

    async def get_active_version(self, workflow_id: str):
        async with get_session() as session:
            repo = WorkflowVersionRepository(session)
            return await repo.get_active_version(workflow_id)

    async def set_active_version(self, workflow_id: str, version_id: str):
        async with get_session() as session:
            repo = WorkflowRepository(session)
            return await repo.set_active_version(workflow_id, version_id)


class ExecutionService:
    async def execute_workflow(self, workflow_id: str, version_id: str, definition: dict, trigger_data: Optional[dict] = None):
        return await execute_workflow(workflow_id, version_id, definition, trigger_data or {})

    async def get_execution(self, execution_id: str):
        async with get_session() as session:
            repo = ExecutionRepository(session)
            return await repo.get(execution_id)

    async def get_execution_with_nodes(self, execution_id: str):
        async with get_session() as session:
            repo = ExecutionRepository(session)
            return await repo.get_with_nodes(execution_id)

    async def list_executions(self, workflow_id: Optional[str] = None, limit: int = 50, offset: int = 0):
        async with get_session() as session:
            repo = ExecutionRepository(session)
            executions = await repo.list(workflow_id, limit, offset)
            total = await repo.count(workflow_id)
            return executions, total