"""Tests for SlackTrigger."""

from typing import cast

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger


def test_slack_trigger__basic():
    """SlackTrigger parses Slack payload correctly."""
    # GIVEN a Slack event payload
    slack_payload = {
        "event": {
            "type": "message",
            "text": "Hello world!",
            "channel": "C123456",
            "user": "U123456",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we create a trigger instance
    trigger = SlackTrigger(slack_payload)

    # THEN trigger attributes contain the correct data
    assert trigger.message == "Hello world!"
    assert trigger.channel == "C123456"
    assert trigger.user == "U123456"
    assert trigger.timestamp == "1234567890.123456"
    assert trigger.thread_ts is None
    assert trigger.event_type == "message"

    # AND the trigger can bind values to workflow state
    state = BaseState()
    trigger.bind_to_state(state)
    stored = state.meta.trigger_attributes
    message_ref = cast(TriggerAttributeReference[str], SlackTrigger.message)
    assert message_ref in stored
    assert stored[message_ref] == "Hello world!"


def test_slack_trigger__with_thread():
    """SlackTrigger handles threaded messages."""
    # GIVEN a Slack event payload with thread_ts
    slack_payload = {
        "event": {
            "type": "message",
            "text": "Reply in thread",
            "channel": "C123456",
            "user": "U123456",
            "ts": "1234567891.123456",
            "thread_ts": "1234567890.123456",
        }
    }

    # WHEN we create a trigger instance
    trigger = SlackTrigger(slack_payload)

    # THEN thread_ts is populated
    assert trigger.thread_ts == "1234567890.123456"


def test_slack_trigger__empty_payload():
    """SlackTrigger handles empty payload gracefully."""
    # GIVEN an empty payload
    slack_payload: dict[str, str] = {}

    # WHEN we create a trigger instance
    trigger = SlackTrigger(slack_payload)

    # THEN it returns empty strings for required fields
    assert trigger.message == ""
    assert trigger.channel == ""
    assert trigger.user == ""
    assert trigger.timestamp == ""
    assert trigger.thread_ts is None
    assert trigger.event_type == "message"  # default value


def test_slack_trigger__app_mention():
    """SlackTrigger handles app_mention events."""
    # GIVEN an app_mention event
    slack_payload = {
        "event": {
            "type": "app_mention",
            "text": "<@U0LAN0Z89> is it everything a river should be?",
            "channel": "C123456",
            "user": "U123456",
            "ts": "1234567890.123456",
        }
    }

    # WHEN we create a trigger instance
    trigger = SlackTrigger(slack_payload)

    # THEN event_type is app_mention
    assert trigger.event_type == "app_mention"
    assert trigger.message == "<@U0LAN0Z89> is it everything a river should be?"


def test_slack_trigger__attributes():
    """SlackTrigger has correct attributes."""
    # GIVEN SlackTrigger class
    # THEN it exposes attribute references for annotated fields
    reference = SlackTrigger.message
    assert isinstance(reference, TriggerAttributeReference)
    assert reference.name == "message"
    assert SlackTrigger.message is reference  # cache returns same reference

    annotations = SlackTrigger.__annotations__
    assert set(annotations) >= {"message", "channel", "user", "timestamp", "thread_ts", "event_type"}

    # AND references resolve when present on state
    state = BaseState()
    state.meta.trigger_attributes[reference] = "Hello"
    assert reference.resolve(state) == "Hello"


def test_slack_trigger__graph_syntax():
    """SlackTrigger can be used in graph syntax."""

    # GIVEN a node
    class TestNode(BaseNode):
        pass

    # WHEN we use SlackTrigger >> Node syntax
    graph = SlackTrigger >> TestNode

    # THEN a graph is created with trigger edge
    assert graph is not None
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 1
    assert trigger_edges[0].trigger_class == SlackTrigger
    assert trigger_edges[0].to_node == TestNode


def test_slack_trigger__multiple_entrypoints():
    """SlackTrigger works with multiple entry points."""

    # GIVEN multiple nodes
    class NodeA(BaseNode):
        pass

    class NodeB(BaseNode):
        pass

    # WHEN we use SlackTrigger >> {NodeA, NodeB} syntax
    graph = SlackTrigger >> {NodeA, NodeB}

    # THEN both nodes have trigger edges
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 2
    target_nodes = {edge.to_node for edge in trigger_edges}
    assert target_nodes == {NodeA, NodeB}


def test_slack_trigger__trigger_then_graph():
    """SlackTrigger works with trigger >> node >> node syntax."""

    # GIVEN two nodes
    class StartNode(BaseNode):
        pass

    class EndNode(BaseNode):
        pass

    # WHEN we create SlackTrigger >> StartNode >> EndNode
    graph = SlackTrigger >> StartNode >> EndNode

    # THEN the graph has one trigger edge and one regular edge
    trigger_edges = list(graph.trigger_edges)
    assert len(trigger_edges) == 1
    assert trigger_edges[0].trigger_class == SlackTrigger
    assert trigger_edges[0].to_node == StartNode

    edges = list(graph.edges)
    assert len(edges) == 1
    assert edges[0].to_node == EndNode
