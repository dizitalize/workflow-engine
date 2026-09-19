import pytest
from Backend.app.nodes.logic.if_node import IfNode


@pytest.mark.asyncio
async def test_if_equals_true():
    node = IfNode()
    result = await node.execute(None, {"left": "hello", "operator": "equals", "right": "hello"})
    assert result.success is True
    assert result.output["result"] is True
    assert result.output["branch"] == "true"


@pytest.mark.asyncio
async def test_if_equals_false():
    node = IfNode()
    result = await node.execute(None, {"left": "hello", "operator": "equals", "right": "world"})
    assert result.success is True
    assert result.output["result"] is False
    assert result.output["branch"] == "false"


@pytest.mark.asyncio
async def test_if_not_equals():
    node = IfNode()
    result = await node.execute(None, {"left": "hello", "operator": "not_equals", "right": "world"})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_contains_string():
    node = IfNode()
    result = await node.execute(None, {"left": "hello world", "operator": "contains", "right": "world"})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_contains_list():
    node = IfNode()
    result = await node.execute(None, {"left": ["a", "b", "c"], "operator": "contains", "right": "b"})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_greater_than():
    node = IfNode()
    result = await node.execute(None, {"left": 10, "operator": "greater_than", "right": 5})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_less_than():
    node = IfNode()
    result = await node.execute(None, {"left": 3, "operator": "less_than", "right": 5})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_exists():
    node = IfNode()
    result = await node.execute(None, {"left": "value", "operator": "exists"})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_not_exists():
    node = IfNode()
    result = await node.execute(None, {"left": None, "operator": "not_exists"})
    assert result.success is True
    assert result.output["result"] is True


@pytest.mark.asyncio
async def test_if_unknown_operator():
    node = IfNode()
    result = await node.execute(None, {"left": "a", "operator": "unknown", "right": "b"})
    assert result.success is False
    assert "Unknown operator" in result.error