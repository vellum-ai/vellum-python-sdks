import os

from vellum.workflows.references.environment_variable import EnvironmentVariableReference

from tests.workflows.environment_variable_node_inputs.workflow import (
    EnvironmentVariableNodeInputsWorkflow,
    NodeWithEnvironmentVariable,
)


def test_environment_variable_resolves_correctly():
    """
    Tests that environment variables resolve to their actual values during node execution.
    """

    os.environ["TEST_API_KEY"] = "secret-key-12345"

    workflow = EnvironmentVariableNodeInputsWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs == {"final_value": "secret-key-12345"}


def test_environment_variable_obfuscated_in_node_inputs():
    """
    Tests that node._inputs keeps environment variable references obfuscated
    rather than exposing the actual values.
    """

    os.environ["TEST_API_KEY"] = "secret-key-12345"

    node = NodeWithEnvironmentVariable()

    api_key_ref = NodeWithEnvironmentVariable.api_key
    assert api_key_ref in node._inputs

    assert isinstance(node._inputs[api_key_ref], EnvironmentVariableReference)

    assert node._inputs[api_key_ref].name == "TEST_API_KEY"

    assert node.api_key == "secret-key-12345"
