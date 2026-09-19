import pytest
from Backend.app.workflow.registry import NodeRegistry
from Backend.app.workflow.validator import GraphValidator
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult
from Backend.app.nodes.triggers.manual import ManualTriggerNode


class ValidNode(BaseNode):
    metadata = NodeMetadata(
        type="test.valid",
        version=1,
        name="Valid Node",
        description="Test",
        category="test",
        config_schema={"type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"]},
    )

    async def execute(self, context, input_data):
        return NodeResult(output={}, success=True)


class NodeWithoutConfigSchema(BaseNode):
    metadata = NodeMetadata(
        type="test.no_schema",
        version=1,
        name="No Schema Node",
        description="Test",
        category="test",
    )

    async def execute(self, context, input_data):
        return NodeResult(output={}, success=True)


@pytest.fixture
def registry():
    r = NodeRegistry()
    r.register(ValidNode)
    r.register(NodeWithoutConfigSchema)
    r.register(ManualTriggerNode)
    return r


@pytest.fixture
def validator(registry):
    return GraphValidator(registry)


def test_validator_passes_valid_graph(validator):
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "node1", "type": "test.valid", "version": 1, "config": {"value": "test"}},
        ],
        "edges": [
            {"source": "trigger", "target": "node1"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validator_fails_missing_source(validator):
    definition = {
        "nodes": [
            {"id": "node1", "type": "test.valid", "version": 1, "config": {"value": "test"}},
        ],
        "edges": [
            {"source": "missing", "target": "node1"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "MISSING_SOURCE_NODE" for e in result.errors)


def test_validator_fails_missing_target(validator):
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
        ],
        "edges": [
            {"source": "trigger", "target": "missing"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "MISSING_TARGET_NODE" for e in result.errors)


def test_validator_fails_invalid_node_type(validator):
    definition = {
        "nodes": [
            {"id": "node1", "type": "invalid.type", "version": 1, "config": {}},
        ],
        "edges": [],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "INVALID_NODE_TYPE" for e in result.errors)


def test_validator_fails_duplicate_node_ids(validator):
    definition = {
        "nodes": [
            {"id": "node1", "type": "test.valid", "version": 1, "config": {"value": "a"}},
            {"id": "node1", "type": "test.valid", "version": 1, "config": {"value": "b"}},
        ],
        "edges": [],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "DUPLICATE_NODE_ID" for e in result.errors)


def test_validator_fails_cycle(validator):
    definition = {
        "nodes": [
            {"id": "a", "type": "test.valid", "version": 1, "config": {"value": "a"}},
            {"id": "b", "type": "test.valid", "version": 1, "config": {"value": "b"}},
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "CYCLE_DETECTED" for e in result.errors)


def test_validator_fails_invalid_config(validator):
    definition = {
        "nodes": [
            {"id": "node1", "type": "test.valid", "version": 1, "config": {}},
        ],
        "edges": [],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "INVALID_CONFIGURATION" for e in result.errors)


def test_validator_passes_node_without_schema(validator):
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "node1", "type": "test.no_schema", "version": 1, "config": {}},
        ],
        "edges": [
            {"source": "trigger", "target": "node1"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is True


def test_validator_fails_unreachable(validator):
    definition = {
        "nodes": [
            {"id": "trigger", "type": "trigger.manual", "version": 1, "config": {}},
            {"id": "node1", "type": "test.valid", "version": 1, "config": {"value": "test"}},
            {"id": "unreachable", "type": "test.valid", "version": 1, "config": {"value": "test"}},
        ],
        "edges": [
            {"source": "trigger", "target": "node1"},
        ],
    }
    result = validator.validate(definition)
    assert result.valid is False
    assert any(e.code == "UNREACHABLE_NODE" for e in result.errors)