import pytest
from Backend.app.schemas.node import NodeDefinition, EdgeDefinition
from Backend.app.workflow.graph import WorkflowGraph


def make_node(node_id: str, node_type: str = "test.node") -> NodeDefinition:
    return NodeDefinition(id=node_id, type=node_type, version=1, config={})


def make_edge(source: str, target: str, source_handle: str = None) -> EdgeDefinition:
    return EdgeDefinition(source=source, target=target, source_handle=source_handle)


def test_graph_get_node():
    nodes = [make_node("a"), make_node("b")]
    edges = [make_edge("a", "b")]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    node = graph.get_node("a")
    assert node is not None
    assert node.id == "a"

    missing = graph.get_node("missing")
    assert missing is None


def test_graph_get_next_nodes():
    nodes = [make_node("a"), make_node("b"), make_node("c")]
    edges = [make_edge("a", "b"), make_edge("a", "c")]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    next_nodes = graph.get_next_nodes("a")
    assert len(next_nodes) == 2
    ids = {n.id for n in next_nodes}
    assert ids == {"b", "c"}


def test_graph_get_previous_nodes():
    nodes = [make_node("a"), make_node("b"), make_node("c")]
    edges = [make_edge("a", "c"), make_edge("b", "c")]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    prev_nodes = graph.get_previous_nodes("c")
    assert len(prev_nodes) == 2
    ids = {n.id for n in prev_nodes}
    assert ids == {"a", "b"}


def test_graph_get_trigger_nodes():
    nodes = [
        make_node("trigger1", "trigger.manual"),
        make_node("set1", "transform.set"),
        make_node("trigger2", "trigger.webhook"),
    ]
    edges = [make_edge("trigger1", "set1")]
    graph = WorkflowGraph(nodes=nodes, edges=edges)

    triggers = graph.get_trigger_nodes()
    assert len(triggers) == 2
    ids = {n.id for n in triggers}
    assert ids == {"trigger1", "trigger2"}