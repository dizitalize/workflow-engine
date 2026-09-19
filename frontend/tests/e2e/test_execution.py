import pytest
from Backend.app.services.workflow_service import WorkflowService, WorkflowVersionService, ExecutionService
from Backend.app.workflow.registry import registry
from Backend.app.nodes.triggers.manual import ManualTriggerNode
from Backend.app.nodes.transform.set_node import SetNode
from Backend.app.nodes.utility.log import LogNode
from Backend.app.nodes.logic.if_node import IfNode


@pytest.fixture(autouse=True)
def setup_registry():
    registry._nodes.clear()
    registry._metadata.clear()
    registry.register(ManualTriggerNode)
    registry.register(SetNode)
    registry.register(LogNode)
    registry.register(IfNode)


@pytest.mark.asyncio
async def test_e2e_hello_world():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    execution_service = ExecutionService()

    workflow = await workflow_service.create_workflow("Hello World", "Test workflow")
    
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "set", "type": "transform.set", "version": 1, "config": {"values": {"name": "Mohan", "message": "Hello World"}}},
            {"id": "log", "type": "utility.log", "version": 1, "config": {"message": "{{set.message}} {{set.name}}"}},
        ],
        "edges": [
            {"source": "trigger", "target": "set"},
            {"source": "set", "target": "log"},
        ],
    }
    
    version = await version_service.create_version(workflow.id, definition)
    await version_service.set_active_version(workflow.id, version.id)
    
    result = await execution_service.execute_workflow(
        workflow.id,
        version.id,
        definition,
        {"topic": "test"}
    )
    
    assert result["status"] == "SUCCESS"
    assert "execution_id" in result
    assert result["output"] is not None


@pytest.mark.asyncio
async def test_e2e_conditional_true_branch():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    execution_service = ExecutionService()

    workflow = await workflow_service.create_workflow("Conditional Test", "Test conditional")
    
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "set", "type": "transform.set", "version": 1, "config": {"values": {"name": "Mohan", "age": 27}}},
            {"id": "condition", "type": "logic.if", "version": 1, "config": {"left": "{{set.age}}", "operator": "greater_than", "right": 18}},
            {"id": "success", "type": "utility.log", "version": 1, "config": {"message": "Adult: {{set.name}}"}},
            {"id": "failure", "type": "utility.log", "version": 1, "config": {"message": "Not adult: {{set.name}}"}},
        ],
        "edges": [
            {"source": "trigger", "target": "set"},
            {"source": "set", "target": "condition"},
            {"source": "condition", "source_handle": "true", "target": "success"},
            {"source": "condition", "source_handle": "false", "target": "failure"},
        ],
    }
    
    version = await version_service.create_version(workflow.id, definition)
    await version_service.set_active_version(workflow.id, version.id)
    
    result = await execution_service.execute_workflow(
        workflow.id,
        version.id,
        definition,
        {}
    )
    
    assert result["status"] == "SUCCESS"
    
    execution = await execution_service.get_execution_with_nodes(result["execution_id"])
    assert execution is not None
    
    node_statuses = {ne.node_id: ne.status for ne in execution.node_executions}
    assert node_statuses["trigger"] == "SUCCESS"
    assert node_statuses["set"] == "SUCCESS"
    assert node_statuses["condition"] == "SUCCESS"
    assert node_statuses["success"] == "SUCCESS"
    assert node_statuses["failure"] == "SKIPPED"


@pytest.mark.asyncio
async def test_e2e_conditional_false_branch():
    workflow_service = WorkflowService()
    version_service = WorkflowVersionService()
    execution_service = ExecutionService()

    workflow = await workflow_service.create_workflow("Conditional Test", "Test conditional")
    
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "set", "type": "transform.set", "version": 1, "config": {"values": {"name": "Child", "age": 10}}},
            {"id": "condition", "type": "logic.if", "version": 1, "config": {"left": "{{set.age}}", "operator": "greater_than", "right": 18}},
            {"id": "success", "type": "utility.log", "version": 1, "config": {"message": "Adult: {{set.name}}"}},
            {"id": "failure", "type": "utility.log", "version": 1, "config": {"message": "Not adult: {{set.name}}"}},
        ],
        "edges": [
            {"source": "trigger", "target": "set"},
            {"source": "set", "target": "condition"},
            {"source": "condition", "source_handle": "true", "target": "success"},
            {"source": "condition", "source_handle": "false", "target": "failure"},
        ],
    }
    
    version = await version_service.create_version(workflow.id, definition)
    await version_service.set_active_version(workflow.id, version.id)
    
    result = await execution_service.execute_workflow(
        workflow.id,
        version.id,
        definition,
        {}
    )
    
    assert result["status"] == "SUCCESS"
    
    execution = await execution_service.get_execution_with_nodes(result["execution_id"])
    assert execution is not None
    
    node_statuses = {ne.node_id: ne.status for ne in execution.node_executions}
    assert node_statuses["trigger"] == "SUCCESS"
    assert node_statuses["set"] == "SUCCESS"
    assert node_statuses["condition"] == "SUCCESS"
    assert node_statuses["success"] == "SKIPPED"
    assert node_statuses["failure"] == "SUCCESS"