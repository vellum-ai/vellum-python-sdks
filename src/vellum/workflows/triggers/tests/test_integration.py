"""Tests for IntegrationTrigger base class."""

import pytest

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.triggers.integration import IntegrationTrigger


def test_integration_trigger__is_abstract():
    """IntegrationTrigger cannot be instantiated directly (ABC)."""
    # WHEN we try to call process_event on IntegrationTrigger directly
    # THEN it raises NotImplementedError
    with pytest.raises(NotImplementedError, match="must implement process_event"):
        IntegrationTrigger.process_event({})


def test_integration_trigger__can_be_instantiated():
    """IntegrationTrigger can be instantiated for testing."""

    # GIVEN IntegrationTrigger with concrete implementation
    class TestTrigger(IntegrationTrigger):
        pass

    # THEN it can be instantiated (even though base is ABC, concrete subclasses work)
    assert TestTrigger is not None


def test_integration_trigger__can_be_subclassed():
    """IntegrationTrigger can be subclassed to create concrete triggers."""

    # GIVEN a concrete implementation of IntegrationTrigger
    class TestTrigger(IntegrationTrigger):
        data: str

        @classmethod
        def process_event(cls, event_data: dict):
            trigger = cls()
            trigger.data = event_data.get("data", "")
            return trigger

    # WHEN we process an event
    result = TestTrigger.process_event({"data": "test"})

    # THEN it returns the expected trigger instance with populated attributes
    assert result.data == "test"


def test_integration_trigger__graph_syntax():
    """IntegrationTrigger can be used in graph syntax."""

    # GIVEN a concrete trigger and a node
    class TestTrigger(IntegrationTrigger):
        value: str

        @classmethod
        def process_event(cls, event_data: dict):
            trigger = cls()
            trigger.value = event_data.get("value", "")
            return trigger

    class TestNode(BaseNode):
        pass

    # WHEN we use trigger >> node syntax
    graph = TestTrigger >> TestNode

    # THEN a graph is created
    assert graph is not None
    assert len(list(graph.trigger_edges)) == 1
    assert list(graph.trigger_edges)[0].trigger_class == TestTrigger
    assert list(graph.trigger_edges)[0].to_node == TestNode


def test_integration_trigger__multiple_entrypoints():
    """IntegrationTrigger works with multiple entry points."""

    # GIVEN a trigger and multiple nodes
    class TestTrigger(IntegrationTrigger):
        msg: str

        @classmethod
        def process_event(cls, event_data: dict):
            trigger = cls()
            trigger.msg = event_data.get("msg", "")
            return trigger

    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # WHEN we use trigger >> {nodes} syntax
    graph = TestTrigger >> {NodeA, NodeB}

    # THEN both nodes are entrypoints
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 2
    target_nodes = {edge.to_node for edge in trigger_edges}
    assert target_nodes == {NodeA, NodeB}


def test_integration_trigger__config_attribute():
    """IntegrationTrigger has optional config attribute."""

    # GIVEN IntegrationTrigger
    # THEN it has a config class variable
    assert hasattr(IntegrationTrigger, "config")
    assert IntegrationTrigger.config is None
