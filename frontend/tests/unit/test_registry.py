import pytest
from Backend.app.workflow.registry import NodeRegistry
from Backend.app.nodes.base import BaseNode, NodeMetadata, NodeResult


class TestNode(BaseNode):
    metadata = NodeMetadata(
        type="test.node",
        version=1,
        name="Test Node",
        description="Test",
        category="test",
    )

    async def execute(self, context, input_data):
        return NodeResult(output={"test": "ok"}, success=True)


def test_registry_register():
    registry = NodeRegistry()
    registry.register(TestNode)
    assert registry.exists("test.node")


def test_registry_get():
    registry = NodeRegistry()
    registry.register(TestNode)
    node_class = registry.get("test.node")
    assert node_class == TestNode


def test_registry_get_metadata():
    registry = NodeRegistry()
    registry.register(TestNode)
    metadata = registry.get_metadata("test.node")
    assert metadata.type == "test.node"
    assert metadata.name == "Test Node"


def test_registry_list():
    registry = NodeRegistry()
    registry.register(TestNode)
    nodes = registry.list()
    assert len(nodes) == 1
    assert nodes[0].type == "test.node"