import pytest
from Backend.app.nodes.transform.set_node import SetNode


@pytest.mark.asyncio
async def test_set_node():
    node = SetNode()
    result = await node.execute(None, {"values": {"name": "Mohan", "age": 27}})
    assert result.success is True
    assert result.output["name"] == "Mohan"
    assert result.output["age"] == 27


@pytest.mark.asyncio
async def test_set_node_empty():
    node = SetNode()
    result = await node.execute(None, {"values": {}})
    assert result.success is True
    assert result.output == {}


@pytest.mark.asyncio
async def test_set_node_nested():
    node = SetNode()
    result = await node.execute(None, {"values": {"user": {"name": "Mohan", "email": "test@example.com"}}})
    assert result.success is True
    assert result.output["user"]["name"] == "Mohan"