from typing import Optional
from uuid import uuid4
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from Backend.app.db.models import Workflow, WorkflowVersion, WorkflowExecution, NodeExecution, WorkflowStatus


class WorkflowRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, description: Optional[str] = None) -> Workflow:
        workflow = Workflow(
            id=str(uuid4()),
            name=name,
            description=description,
            status=WorkflowStatus.DRAFT,
        )
        self.session.add(workflow)
        await self.session.flush()
        return workflow

    async def get(self, workflow_id: str) -> Optional[Workflow]:
        result = await self.session.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50, offset: int = 0) -> list[Workflow]:
        result = await self.session.execute(
            select(Workflow).limit(limit).offset(offset).order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(Workflow.id)))
        return result.scalar_one()

    async def update(self, workflow_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Workflow]:
        workflow = await self.get(workflow_id)
        if not workflow:
            return None
        if name is not None:
            workflow.name = name
        if description is not None:
            workflow.description = description
        await self.session.flush()
        return workflow

    async def set_status(self, workflow_id: str, status: WorkflowStatus) -> Optional[Workflow]:
        workflow = await self.get(workflow_id)
        if not workflow:
            return None
        workflow.status = status
        await self.session.flush()
        return workflow

    async def set_active_version(self, workflow_id: str, version_id: str) -> Optional[Workflow]:
        workflow = await self.get(workflow_id)
        if not workflow:
            return None
        workflow.active_version_id = version_id
        await self.session.flush()
        return workflow

    async def delete(self, workflow_id: str) -> bool:
        workflow = await self.get(workflow_id)
        if not workflow:
            return False
        await self.session.delete(workflow)
        await self.session.flush()
        return True


class WorkflowVersionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workflow_id: str, definition: dict) -> WorkflowVersion:
        result = await self.session.execute(
            select(func.max(WorkflowVersion.version)).where(WorkflowVersion.workflow_id == workflow_id)
        )
        max_version = result.scalar_one_or_none() or 0
        new_version = max_version + 1

        version = WorkflowVersion(
            id=str(uuid4()),
            workflow_id=workflow_id,
            version=new_version,
            definition=definition,
        )
        self.session.add(version)
        await self.session.flush()
        return version

    async def get(self, version_id: str) -> Optional[WorkflowVersion]:
        result = await self.session.execute(
            select(WorkflowVersion).where(WorkflowVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_by_workflow_and_version(self, workflow_id: str, version: int) -> Optional[WorkflowVersion]:
        result = await self.session.execute(
            select(WorkflowVersion).where(
                WorkflowVersion.workflow_id == workflow_id,
                WorkflowVersion.version == version
            )
        )
        return result.scalar_one_or_none()

    async def list_by_workflow(self, workflow_id: str) -> list[WorkflowVersion]:
        result = await self.session.execute(
            select(WorkflowVersion).where(WorkflowVersion.workflow_id == workflow_id).order_by(WorkflowVersion.version.desc())
        )
        return list(result.scalars().all())

    async def get_active_version(self, workflow_id: str) -> Optional[WorkflowVersion]:
        from Backend.app.db.models import Workflow
        result = await self.session.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        workflow = result.scalar_one_or_none()
        if workflow and workflow.active_version_id:
            return await self.get(workflow.active_version_id)
        return None


class ExecutionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workflow_id: str, version_id: str, trigger_data: Optional[dict] = None) -> WorkflowExecution:
        from Backend.app.db.models import ExecutionStatus
        execution = WorkflowExecution(
            id=str(uuid4()),
            workflow_id=workflow_id,
            version_id=version_id,
            status=ExecutionStatus.PENDING,
            trigger_data=trigger_data,
        )
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def get(self, execution_id: str) -> Optional[WorkflowExecution]:
        result = await self.session.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def get_with_nodes(self, execution_id: str) -> Optional[WorkflowExecution]:
        result = await self.session.execute(
            select(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .options(selectinload(WorkflowExecution.node_executions))
        )
        return result.scalar_one_or_none()

    async def list(self, workflow_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> list[WorkflowExecution]:
        query = select(WorkflowExecution).limit(limit).offset(offset).order_by(WorkflowExecution.created_at.desc())
        if workflow_id:
            query = query.where(WorkflowExecution.workflow_id == workflow_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, workflow_id: Optional[str] = None) -> int:
        query = select(func.count(WorkflowExecution.id))
        if workflow_id:
            query = query.where(WorkflowExecution.workflow_id == workflow_id)
        result = await self.session.execute(query)
        return result.scalar_one()