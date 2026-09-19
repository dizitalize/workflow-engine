import pytest
from Backend.app.workflow.expressions import resolve_variables


def test_resolve_simple_variable():
    context = {"trigger": {"name": "Mohan"}, "execution": {"id": "exec_123"}}
    result = resolve_variables("Hello {{trigger.name}}", context)
    assert result == "Hello Mohan"


def test_resolve_execution_id():
    context = {"execution": {"id": "exec_123"}}
    result = resolve_variables("ID: {{execution.id}}", context)
    assert result == "ID: exec_123"


def test_resolve_nested_object():
    context = {"node_1": {"customer": {"name": "Mohan", "email": "test@example.com"}}}
    result = resolve_variables("{{node_1.customer.name}}", context)
    assert result == "Mohan"


def test_resolve_in_dict():
    context = {"set_1": {"name": "Mohan"}}
    value = {"message": "Hello {{set_1.name}}", "data": {"email": "test@example.com"}}
    result = resolve_variables(value, context)
    assert result["message"] == "Hello Mohan"
    assert result["data"]["email"] == "test@example.com"


def test_resolve_in_list():
    context = {"set_1": {"items": ["a", "b", "c"]}}
    value = ["{{set_1.items}}", "static"]
    result = resolve_variables(value, context)
    assert result == [["a", "b", "c"], "static"]


def test_resolve_missing_variable_returns_original():
    context = {"trigger": {"name": "Mohan"}}
    result = resolve_variables("Hello {{missing.variable}}", context)
    assert result == "Hello {{missing.variable}}"


def test_resolve_no_variables_returns_original():
    context = {"trigger": {"name": "Mohan"}}
    result = resolve_variables("No variables here", context)
    assert result == "No variables here"


def test_resolve_nested_variables():
    context = {"a": {"b": {"c": "deep"}}}
    result = resolve_variables("{{a.b.c}}", context)
    assert result == "deep"


def test_resolve_number_values():
    context = {"set_1": {"age": 27, "score": 95.5}}
    result = resolve_variables("Age: {{set_1.age}}, Score: {{set_1.score}}", context)
    assert result == "Age: 27, Score: 95.5"