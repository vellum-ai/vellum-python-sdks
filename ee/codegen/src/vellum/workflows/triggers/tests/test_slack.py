"""Tests for SlackTrigger."""

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.triggers.slack import SlackTrigger


def test_slack_trigger__process_event__basic():
    """SlackTrigger.process_event parses Slack payload correctly."""
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

    # WHEN we process the event
    outputs = SlackTrigger.process_event(slack_payload)

    # THEN outputs contain the correct data
    assert outputs.message == "Hello world!"
    assert outputs.channel == "C123456"
    assert outputs.user == "U123456"
    assert outputs.timestamp == "1234567890.123456"
    assert outputs.thread_ts is None
    assert outputs.event_type == "message"


def test_slack_trigger__process_event__with_thread():
    """SlackTrigger.process_event handles threaded messages."""
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

    # WHEN we process the event
    outputs = SlackTrigger.process_event(slack_payload)

    # THEN thread_ts is populated
    assert outputs.thread_ts == "1234567890.123456"


def test_slack_trigger__process_event__empty_payload():
    """SlackTrigger.process_event handles empty payload gracefully."""
    # GIVEN an empty payload
    slack_payload = {}

    # WHEN we process the event
    outputs = SlackTrigger.process_event(slack_payload)

    # THEN it returns empty strings for required fields
    assert outputs.message == ""
    assert outputs.channel == ""
    assert outputs.user == ""
    assert outputs.timestamp == ""
    assert outputs.thread_ts is None
    assert outputs.event_type == "message"  # default value


def test_slack_trigger__process_event__app_mention():
    """SlackTrigger.process_event handles app_mention events."""
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

    # WHEN we process the event
    outputs = SlackTrigger.process_event(slack_payload)

    # THEN event_type is app_mention
    assert outputs.event_type == "app_mention"
    assert outputs.message == "<@U0LAN0Z89> is it everything a river should be?"


def test_slack_trigger__outputs_class():
    """SlackTrigger.Outputs has correct fields."""
    # GIVEN SlackTrigger.Outputs
    # THEN it has all expected fields
    assert hasattr(SlackTrigger.Outputs, "__annotations__")
    annotations = SlackTrigger.Outputs.__annotations__
    assert "message" in annotations
    assert "channel" in annotations
    assert "user" in annotations
    assert "timestamp" in annotations
    assert "thread_ts" in annotations
    assert "event_type" in annotations


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
