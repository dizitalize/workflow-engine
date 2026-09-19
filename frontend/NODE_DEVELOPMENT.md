# Node Development Guide

## Creating a New Node

### 1. Choose Category

Nodes are organized by category:
- `triggers/` - Workflow starters (manual, schedule, webhook)
- `logic/` - Flow control (if, switch, loop)
- `transform/` - Data transformation (set, map, json)
- `utility/` - General utilities (log, http, delay)
- `ai/` - AI operations (future)
- `communication/` - Email, Slack, etc. (future)
- `social/` - Instagram, Facebook, etc. (future)
- `data/` - Database, sheets (future)

### 2. Create Node File

Create `app/nodes/<category>/<name>.py`:

```python
from typing import Any
from app.nodes.base import BaseNode, NodeMetadata, NodeResult


class MyNode(BaseNode):
    metadata = NodeMetadata(
        type="category.my_node",
        version=1,
        name="My Node",
        description="What this node does",
        category="category",
        config_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "number"},
            },
            "required": ["param1"],
        },
        inputs=[
            {"name": "input1", "type": "string", "description": "Input description"}
        ],
        outputs=[
            {"name": "output1", "type": "string", "description": "Output description"}
        ],
    )

    async def execute(self, context: Any, input_data: Any) -> NodeResult:
        # input_data contains resolved config
        param1 = input_data.get("param1")
        param2 = input_data.get("param2", 0)
        
        # Do work...
        result = {"processed": param1, "count": param2}
        
        return NodeResult(output=result, success=True)
```

### 3. Register Node

Add to `app/nodes/__init__.py`:

```python
from app.nodes.category.my_node import MyNode

def register_nodes():
    # ... existing registrations
    registry.register(MyNode)
```

### 4. Test Node

```bash
pytest tests/unit/test_my_node.py
```

## BaseNode Contract

```python
class BaseNode:
    metadata: NodeMetadata  # Required class attribute
    
    async def execute(self, context, input_data) -> NodeResult:
        # Implementation required
        pass
    
    def validate_config(self, config) -> list[str]:
        # Optional: return list of error messages
        return []
```

## NodeMetadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | str | Yes | Unique identifier (e.g., `transform.set`) |
| version | int | Yes | Node version |
| name | str | Yes | Display name |
| description | str | Yes | Human-readable description |
| category | str | Yes | Category for grouping |
| inputs | list | No | Input port definitions |
| outputs | list | No | Output port definitions |
| config_schema | dict | No | JSON Schema for config validation |

## Execution Context

The `context` parameter in `execute()` provides:

```python
context.execution_id      # Unique execution ID
context.workflow_id       # Workflow ID
context.workflow_version_id  # Version ID
context.trigger_data      # Initial trigger input
context.variables         # Workflow variables
context.node_results      # Outputs from previous nodes
context.current_node_id   # Currently executing node ID
```

### Accessing Previous Node Results

```python
# In execute():
previous_output = context.get_node_result("node_id")
# Or:
previous_output = context.node_results.get("node_id")
```

## Variable Resolution

Node configurations are automatically resolved before execution:

```json
{
  "message": "Hello {{trigger.name}}",
  "data": {
    "email": "{{set_1.email}}"
  },
  "items": ["{{set_1.item}}"]
}
```

The engine resolves all `{{...}}` patterns recursively.

## NodeResult

Return `NodeResult` from `execute()`:

```python
NodeResult(
    output={"key": "value"},  # Data passed to next nodes
    error=None,               # Error message if failed
    success=True              # Execution status
)
```

## Config Validation

Override `validate_config()` for custom validation:

```python
def validate_config(self, config: dict) -> list[str]:
    errors = []
    if not config.get("required_field"):
        errors.append("required_field is required")
    if config.get("count", 0) < 0:
        errors.append("count must be positive")
    return errors
```

## Best Practices

1. **Keep nodes small** - Single responsibility
2. **No external dependencies in base** - Only in node implementation
3. **Handle errors gracefully** - Return `NodeResult(success=False, error="...")`
4. **Use config_schema** - Enables frontend form generation
5. **Document inputs/outputs** - For visual editor
6. **No global state** - Each execution is isolated
7. **Async where appropriate** - Use `httpx` for HTTP, not `requests`

## Example: HTTP Request Node

```python
class HttpRequestNode(BaseNode):
    metadata = NodeMetadata(
        type="utility.http_request",
        version=1,
        name="HTTP Request",
        description="Make HTTP requests",
        category="utility",
        config_schema={
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
                "url": {"type": "string", "format": "uri"},
                "headers": {"type": "object"},
                "params": {"type": "object"},
                "body": {},
                "timeout": {"type": "number", "default": 30},
            },
            "required": ["method", "url"],
        },
    )

    async def execute(self, context, input_data):
        # Implementation...
        return NodeResult(output=response_data, success=True)
```

## Testing Nodes

```python
import pytest
from app.nodes.utility.my_node import MyNode


@pytest.mark.asyncio
async def test_my_node():
    node = MyNode()
    result = await node.execute(None, {"param1": "test", "param2": 5})
    assert result.success is True
    assert result.output["processed"] == "test"
```