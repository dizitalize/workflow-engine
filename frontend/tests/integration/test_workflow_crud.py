import pytest
from Backend.app.services.workflow_service import WorkflowService, WorkflowVersionService
from Backend.app.workflow.registry import registry
from Backend.app.nodes.triggers.manual import ManualTriggerNode
from Backend.app.nodes.transform.set_node import SetNode
from Backend.app.nodes.utility.log import LogNode
from Backend.app.nodes.logic.if_node import IfNode
from Backend.app.db.database import async_session_maker
from Backend.app.db.models import Workflow, WorkflowVersion, WorkflowExecution, NodeExecution
from sqlalchemy import delete


@pytest.fixture(autouse=True)
async def clean_db():
    # Clean up before each test
    async with async_session_maker() as session:
        await session.execute(delete(NodeExecution))
        await session.execute(delete(WorkflowExecution))
        await session.execute(delete(WorkflowVersion))
        await session.execute(delete(Workflow))
        await session.commit()


@pytest.fixture(autouse=True)
def setup_registry():
    registry._nodes.clear()
    registry._metadata.clear()
    registry.register(ManualTriggerNode)
    registry.register(SetNode)
    registry.register(LogNode)
    registry.register(IfNode)


@pytest.mark.asyncio
async def test_create_workflow():
    service = WorkflowService()
    workflow = await service.create_workflow("Test Workflow", "Description")
    assert workflow.id is not None
    assert workflow.name == "Test Workflow"
    assert workflow.description == "Description"
    assert workflow.status.value == "DRAFT"


@pytest.mark.asyncio
async def test_get_workflow():
    service = WorkflowService()
    created = await service.create_workflow("Test")
    retrieved = await service.get_workflow(created.id)
    assert retrieved.id == created.id
    assert retrieved.name == "Test"


@pytest.mark.asyncio
async def test_list_workflows():
    service = WorkflowService()
    await service.create_workflow("Workflow 1")
    await service.create_workflow("Workflow 2")
    workflows, total = await service.list_workflows(limit=10, offset=0)
    assert total == 2
    assert len(workflows) == 2


@pytest.mark.asyncio
async def test_update_workflow():
    service = WorkflowService()
    created = await service.create_workflow("Original")
    updated = await service.update_workflow(created.id, name="Updated")
    assert updated.name == "Updated"


@pytest.mark.asyncio
async def test_delete_workflow():
    service = WorkflowService()
    created = await service.create_workflow("To Delete")
    deleted = await service.delete_workflow(created.id)
    assert deleted is True
    retrieved = await service.get_workflow(created.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_create_version():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    
    workflow = await workflow_service.create_workflow("Test")
    version = await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    assert version.id is not None
    assert version.workflow_id == workflow.id
    assert version.version == 1


@pytest.mark.asyncio
async def test_version_increment():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    
    workflow = await workflow_service.create_workflow("Test")
    v1 = await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    v2 = await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    v3 = await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    
    assert v1.version == 1
    assert v2.version == 2
    assert v3.version == 3


@pytest.mark.asyncio
async def test_list_versions():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    
    workflow = await workflow_service.create_workflow("Test")
    await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    await version_service.create_version(workflow.id, {"nodes": [], "edges": []})
    
    versions = await version_service.list_versions(workflow.id)
    assert len(versions) == 2
    assert versions[0].version == 2
    assert versions[1].version == 1