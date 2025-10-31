"""Tests for IntegrationTrigger base class."""

from typing import Any

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.integration import IntegrationTrigger


def test_integration_trigger__can_be_instantiated_as_base():
    """IntegrationTrigger can be instantiated as a base class."""
    # WHEN we instantiate IntegrationTrigger directly
    trigger = IntegrationTrigger(test="data")

    # THEN it creates an instance with event data stored
    assert trigger._event_data == {"test": "data"}


def test_integration_trigger__can_be_instantiated():
    """IntegrationTrigger can be instantiated for testing."""

    # GIVEN IntegrationTrigger with concrete implementation
    class TestTrigger(IntegrationTrigger):
        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

    # THEN it can be instantiated (even though base is ABC, concrete subclasses work)
    assert TestTrigger is not None


def test_integration_trigger__can_be_subclassed():
    """IntegrationTrigger can be subclassed to create concrete triggers."""

    # GIVEN a concrete implementation of IntegrationTrigger
    class TestTrigger(IntegrationTrigger):
        data: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        def __init__(self, **kwargs: Any):
            super().__init__(**kwargs)
            self.data = kwargs.get("data", "")

    # WHEN we create a trigger instance
    result = TestTrigger(data="test")

    # THEN it returns the expected trigger instance with populated attributes
    assert result.data == "test"


def test_integration_trigger__attribute_reference():
    """Trigger annotations expose TriggerAttributeReference descriptors."""

    class TestTrigger(IntegrationTrigger):
        value: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        def __init__(self, **kwargs: Any):
            super().__init__(**kwargs)
            self.value = kwargs.get("value", "")

    reference = TestTrigger.value
    assert isinstance(reference, TriggerAttributeReference)
    assert reference.name == "value"
    assert TestTrigger.value == reference
    assert reference == TestTrigger.attribute_references()["value"]

    state = BaseState()
    trigger = TestTrigger(value="data")
    trigger.bind_to_state(state)
    assert reference.resolve(state) == "data"


def test_integration_trigger__graph_syntax():
    """IntegrationTrigger can be used in graph syntax."""

    # GIVEN a concrete trigger and a node
    class TestTrigger(IntegrationTrigger):
        value: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        def __init__(self, **kwargs: Any):
            super().__init__(**kwargs)
            self.value = kwargs.get("value", "")

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

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "test"
            slug = "test"

        def __init__(self, **kwargs: Any):
            super().__init__(**kwargs)
            self.msg = kwargs.get("msg", "")

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
    """IntegrationTrigger requires Config class with provider, integration_name, and slug."""

    # GIVEN IntegrationTrigger
    # THEN it has a Config class with type annotations for required fields
    assert hasattr(IntegrationTrigger, "Config")
    assert hasattr(IntegrationTrigger.Config, "__annotations__")
    assert "provider" in IntegrationTrigger.Config.__annotations__
    assert "integration_name" in IntegrationTrigger.Config.__annotations__
    assert "slug" in IntegrationTrigger.Config.__annotations__
