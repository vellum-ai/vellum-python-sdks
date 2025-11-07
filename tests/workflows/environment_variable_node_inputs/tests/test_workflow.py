import os

from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.environment_variable_node_inputs.workflow import (
    EnvironmentVariableNodeInputsWorkflow,
    NodeWithEnvironmentVariable,
)


def test_environment_variable_resolves_correctly():
    """
    Tests that environment variables resolve to their actual values during node execution
    and that the node execution initiated event contains obfuscated representations.
    """

    os.environ["TEST_API_KEY"] = "secret-key-12345"
    os.environ["FOO_API_KEY"] = "foo-secret-67890"

    workflow = EnvironmentVariableNodeInputsWorkflow()

    # WHEN the workflow is streamed
    events = list(workflow.stream(event_filter=root_workflow_event_filter))

    # THEN the workflow should complete successfully
    terminal_event = events[-1]
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {"final_value": "secret-key-12345"}

    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    assert len(node_initiated_events) == 1
    node_initiated_event = node_initiated_events[0]

    api_key_ref = NodeWithEnvironmentVariable.api_key
    assert api_key_ref in node_initiated_event.inputs
    assert node_initiated_event.inputs[api_key_ref] == EnvironmentVariableReference(name="TEST_API_KEY")

    # AND the nested environment variable should also be obfuscated
    other_keys_foo_ref = NodeWithEnvironmentVariable.other_keys["foo"]
    assert other_keys_foo_ref in node_initiated_event.inputs
    assert node_initiated_event.inputs[other_keys_foo_ref] == EnvironmentVariableReference(name="FOO_API_KEY")

    event_dict = node_initiated_event.model_dump()
    assert "body" in event_dict
    assert "inputs" in event_dict["body"]

    serialized_inputs = event_dict["body"]["inputs"]
    assert "api_key" in serialized_inputs
    assert serialized_inputs["api_key"] == {
        "type": "ENVIRONMENT_VARIABLE",
        "environment_variable": "TEST_API_KEY",
    }

    assert "other_keys.foo" in serialized_inputs
    assert serialized_inputs["other_keys.foo"] == {
        "type": "ENVIRONMENT_VARIABLE",
        "environment_variable": "FOO_API_KEY",
    }


def test_environment_variable_obfuscated_in_node_inputs():
    """
    Tests that node._inputs keeps environment variable references obfuscated
    rather than exposing the actual values.
    """

    os.environ["TEST_API_KEY"] = "secret-key-12345"
    os.environ["FOO_API_KEY"] = "foo-secret-67890"

    node = NodeWithEnvironmentVariable()

    # THEN the _inputs should contain obfuscated representations, not the resolved values
    api_key_ref = NodeWithEnvironmentVariable.api_key
    assert api_key_ref in node._inputs
    assert node._inputs[api_key_ref] == EnvironmentVariableReference(name="TEST_API_KEY")

    # AND the nested environment variable should also be obfuscated
    other_keys_foo_ref = NodeWithEnvironmentVariable.other_keys["foo"]
    assert other_keys_foo_ref in node._inputs
    assert node._inputs[other_keys_foo_ref] == EnvironmentVariableReference(name="FOO_API_KEY")

    assert node.api_key == "secret-key-12345"
    assert node.other_keys["foo"] == "foo-secret-67890"
