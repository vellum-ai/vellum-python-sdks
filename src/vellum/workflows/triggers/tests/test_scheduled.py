"""Tests for ScheduledTrigger class."""

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.triggers.scheduled import ScheduledTrigger


def test_scheduled_trigger__can_be_instantiated():
    """
    Tests that ScheduledTrigger can be instantiated.
    """

    trigger = ScheduledTrigger()

    assert trigger is not None


def test_scheduled_trigger__graph_syntax():
    """
    Tests that ScheduledTrigger can be used in graph syntax.
    """

    class TestNode(BaseNode):
        pass

    # WHEN we use trigger >> node syntax
    graph = ScheduledTrigger >> TestNode

    # THEN a graph is created
    assert graph is not None
    assert len(list(graph.trigger_edges)) == 1
    assert list(graph.trigger_edges)[0].trigger_class == ScheduledTrigger
    assert list(graph.trigger_edges)[0].to_node == TestNode


def test_scheduled_trigger__multiple_entrypoints():
    """
    Tests that ScheduledTrigger works with multiple entry points.
    """

    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # WHEN we use trigger >> {nodes} syntax
    graph = ScheduledTrigger >> {NodeA, NodeB}

    # THEN both nodes are entrypoints
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 2
    target_nodes = {edge.to_node for edge in trigger_edges}
    assert target_nodes == {NodeA, NodeB}


def test_scheduled_trigger__attribute_references():
    """
    Tests that ScheduledTrigger has no trigger-specific attributes.
    """

    references = ScheduledTrigger.attribute_references()

    assert references == {}


def test_scheduled_trigger__graph_with_chain():
    """
    Tests that ScheduledTrigger can be used with node chains.
    """

    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    graph = ScheduledTrigger >> (NodeA >> NodeB)

    assert graph is not None
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 1
    assert trigger_edges[0].trigger_class == ScheduledTrigger
    assert trigger_edges[0].to_node == NodeA
