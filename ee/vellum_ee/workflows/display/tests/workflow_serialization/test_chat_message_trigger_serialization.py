"""Tests for ChatMessageTrigger serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.ports import Port
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum_ee.workflows.display.utils.exceptions import TriggerValidationError, WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_simple_chat_workflow_serialization():
    """SimpleChatWorkflow from tests/workflows serializes correctly with ChatMessageTrigger."""

    # GIVEN a Workflow that uses a ChatMessageTrigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleChatWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # AND the triggers should be serialized correctly
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    trigger = triggers[0]
    assert trigger["id"] == "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f"
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND the attributes should include message and name
    attributes = trigger["attributes"]
    assert len(attributes) == 2
    attribute_keys = {attr["key"] for attr in attributes}
    assert attribute_keys == {"message", "name"}

    # AND the exec_config should be correct
    assert trigger["exec_config"] == {
        "output": {
            "type": "WORKFLOW_OUTPUT",
            "output_variable_id": "cc1208e9-c043-47f4-abea-c01ac0dbf04c",
        },
    }

    # AND the display_data should be correct
    assert trigger["display_data"] == {
        "label": "Chat Message",
        "position": {
            "x": 0.0,
            "y": 0.0,
        },
        "z_index": 0,
        "icon": "vellum:icon:message-dots",
        "color": "blue",
    }


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello!"


class ChatTriggerWithoutOutput(ChatMessageTrigger):
    """Chat trigger without Config.output specified."""

    pass


class WorkflowWithUnspecifiedChatTriggerOutput(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow using ChatTrigger without output specified."""

    graph = ChatTriggerWithoutOutput >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response


def test_chat_message_trigger_validation__output_not_specified():
    """
    Tests that serialization adds TriggerValidationError to errors when Chat Trigger output is not specified.
    """

    # GIVEN a Workflow that uses a ChatMessageTrigger without Config.output specified
    workflow_display = get_workflow_display(workflow_class=WorkflowWithUnspecifiedChatTriggerOutput)

    # WHEN we serialize the workflow
    workflow_display.serialize()

    # THEN the display_context should contain a TriggerValidationError
    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 1

    # AND the error should be a TriggerValidationError with the expected message
    error = errors[0]
    assert isinstance(error, TriggerValidationError)
    assert "Chat Trigger output must be specified" in str(error)


def test_chat_message_trigger_graph_with_duplicate_edges():
    """ChatMessageTrigger graph with duplicate edges should deduplicate and report error."""

    # GIVEN a ChatMessageTrigger subclass
    class Chat(ChatMessageTrigger):
        pass

    class Orchestrator(BaseNode):
        pass

    # AND a workflow with a graph containing duplicate edges from trigger to node
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            Chat >> Orchestrator,
            Chat >> Orchestrator,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the workflow should serialize successfully
    assert "workflow_raw_data" in result
    assert "triggers" in result

    # AND there should be a CHAT_MESSAGE trigger
    triggers: list = result["triggers"]
    assert len(triggers) == 1
    assert triggers[0]["type"] == "CHAT_MESSAGE"

    # AND there should NOT be a MANUAL trigger
    manual_triggers = [t for t in triggers if t.get("type") == "MANUAL"]
    assert len(manual_triggers) == 0

    # AND there should NOT be an ENTRYPOINT node
    workflow_raw_data: dict = result["workflow_raw_data"]
    nodes: list = workflow_raw_data["nodes"]
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 0, "ChatMessageTrigger workflows should NOT have an ENTRYPOINT node"

    # AND edges should have unique IDs (no duplicates)
    edges: list = workflow_raw_data["edges"]
    edge_ids = [e["id"] for e in edges if isinstance(e, dict)]
    assert len(edge_ids) == len(set(edge_ids)), f"Duplicate edge IDs found: {edge_ids}"

    # AND there should be an error about the duplicate edge
    errors = list(workflow_display.display_context.errors)
    duplicate_edge_errors = [
        e for e in errors if isinstance(e, WorkflowValidationError) and "duplicate" in str(e).lower()
    ]
    assert len(duplicate_edge_errors) == 1, f"Expected 1 duplicate edge error, got {len(duplicate_edge_errors)}"


def test_graph_with_shared_prefix_different_paths__no_validation_error():
    """Graph with shared prefix but different paths should not produce validation errors."""

    # GIVEN a ChatMessageTrigger subclass as the entry point
    class A(ChatMessageTrigger):
        pass

    # AND nodes for a workflow
    class B(BaseNode):
        pass

    class C(BaseNode):
        pass

    class D(BaseNode):
        pass

    # AND a workflow with a graph containing shared prefix but different paths
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            A >> B >> C,
            A >> B >> D,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the workflow should serialize successfully
    assert "workflow_raw_data" in result

    # AND there should be NO validation errors about duplicates
    errors = list(workflow_display.display_context.errors)
    duplicate_errors = [e for e in errors if isinstance(e, WorkflowValidationError) and "duplicate" in str(e).lower()]
    assert len(duplicate_errors) == 0, f"Expected no duplicate errors, got {len(duplicate_errors)}: {duplicate_errors}"


def test_graph_with_duplicate_paths__validation_error():
    """Graph with duplicate paths should produce a validation error."""

    # GIVEN nodes for a workflow
    class A(BaseNode):
        pass

    class B(BaseNode):
        pass

    class C(BaseNode):
        pass

    # AND a workflow with a graph containing duplicate paths
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            A >> B >> C,
            A >> B >> C,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the workflow should serialize successfully
    assert "workflow_raw_data" in result

    # AND there should be a validation error about the duplicate path
    errors = list(workflow_display.display_context.errors)
    duplicate_errors = [e for e in errors if isinstance(e, WorkflowValidationError) and "duplicate" in str(e).lower()]
    assert len(duplicate_errors) == 1, f"Expected 1 duplicate error, got {len(duplicate_errors)}"


def test_graph_with_different_ports_same_target__no_validation_error():
    """Graph with different ports from same node to same target should not produce validation errors."""

    # GIVEN a node with multiple ports
    class A(BaseNode):
        class Ports(BaseNode.Ports):
            foo = Port()
            bar = Port()

    # AND a target node
    class B(BaseNode):
        pass

    # AND a workflow with a graph where different ports connect to the same target
    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = {
            A.Ports.foo >> B,
            A.Ports.bar >> B,
        }

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the workflow should serialize successfully
    assert "workflow_raw_data" in result

    # AND there should be NO validation errors about duplicates
    errors = list(workflow_display.display_context.errors)
    duplicate_errors = [e for e in errors if isinstance(e, WorkflowValidationError) and "duplicate" in str(e).lower()]
    assert len(duplicate_errors) == 0, f"Expected no duplicate errors, got {len(duplicate_errors)}: {duplicate_errors}"
