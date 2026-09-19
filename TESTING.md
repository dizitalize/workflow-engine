# Testing Guide

## Test Structure

```
tests/
├── unit/           # Unit tests (fast, isolated)
├── integration/    # Integration tests (database, services)
└── e2e/           # End-to-end tests (full workflow execution)
```

## Running Tests

```powershell
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/unit/test_registry.py

# Specific test
pytest tests/unit/test_registry.py::test_registry_register

# Verbose
pytest -v

# Parallel (if pytest-xdist installed)
pytest -n auto
```

## Test Categories

### Unit Tests
- Test single functions/classes in isolation
- Mock external dependencies
- Fast execution (< 100ms each)
- No database required

Key areas:
- `NodeRegistry` - Registration, lookup
- `WorkflowGraph` - Node/edge traversal
- `GraphValidator` - Cycle detection, unreachable nodes
- `ExpressionResolver` - Variable substitution
- Individual nodes - `IfNode`, `SetNode`, `LogNode`

### Integration Tests
- Test service layer with real database
- Use SQLite in-memory or file
- Test CRUD operations
- Test workflow versioning

### E2E Tests
- Full workflow execution
- Multiple nodes chained
- Conditional branching
- Error handling
- Execution persistence

## Test Fixtures

Defined in `tests/conftest.py`:

```python
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    # Creates tables before all tests
    # Drops after all tests

@pytest_asyncio.fixture
async def db_session():
    # Provides transactional session per test
    # Rolls back after each test

@pytest.fixture(autouse=True)
async def clear_registry():
    # Clears node registry before each test
```

## Writing Tests

### Unit Test Example

```python
import pytest
from app.workflow.registry import NodeRegistry


def test_registry_register():
    registry = NodeRegistry()
    registry.register(MyNode)
    assert registry.exists("my.node")
```

### Async Test Example

```python
import pytest
from app.nodes.logic.if_node import IfNode


@pytest.mark.asyncio
async def test_if_equals():
    node = IfNode()
    result = await node.execute(None, {"left": 1, "operator": "equals", "right": 1})
    assert result.success is True
    assert result.output["result"] is True
```

### Integration Test Example

```python
import pytest
from app.services.workflow_service import WorkflowService


@pytest.mark.asyncio
async def test_create_workflow():
    service = WorkflowService()
    workflow = await service.create_workflow("Test")
    assert workflow.name == "Test"
```

## Test Data

- Use fixtures for common test data
- Create helper functions for complex objects
- Keep tests independent

## Continuous Integration

Tests should run on:
- Every commit
- Pull requests
- Before releases

## Coverage Goals

- Unit tests: > 90%
- Integration tests: > 80%
- Overall: > 85%

## Debugging Tests

```powershell
# Run with output
pytest -v -s tests/unit/test_registry.py

# Stop on first failure
pytest -x

# Run failed tests only
pytest --lf
```

## Common Issues

1. **Async tests** - Always use `@pytest.mark.asyncio`
2. **Database cleanup** - Use `db_session` fixture
3. **Registry pollution** - Use `clear_registry` fixture
4. **Event loop** - Configure `asyncio_mode = "auto"` in pytest.ini