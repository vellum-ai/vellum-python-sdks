from unittest.mock import MagicMock

from vellum.client.types.vellum_variable import VellumVariable
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_workflow_deployment_tool_wrapper.workflow import (
    BasicToolCallingNodeWorkflowDeploymentToolWrapperWorkflow,
)


def test_serialize_workflow__workflow_deployment_with_tool_wrapper(vellum_client):
    """
    Tests that a workflow deployment with tool wrapper serializes correctly with definition.
    """

    # GIVEN a workflow that uses a workflow deployment with tool wrapper
    workflow_class = BasicToolCallingNodeWorkflowDeploymentToolWrapperWorkflow

    # AND a mock for the workflow deployment release info
    mock_release = MagicMock()
    mock_release.deployment.name = "weather-workflow-deployment"
    mock_release.description = "A workflow that gets the weather for a given city and date."
    mock_release.workflow_version.input_variables = [
        VellumVariable(
            id="city-id",
            key="city",
            type="STRING",
            required=True,
            default=None,
        ),
        VellumVariable(
            id="date-id",
            key="date",
            type="STRING",
            required=True,
            default=None,
        ),
        VellumVariable(
            id="context-id",
            key="context",
            type="STRING",
            required=False,
            default=None,
        ),
    ]
    vellum_client.workflow_deployments.retrieve_workflow_deployment_release.return_value = mock_release

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=workflow_class)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should include both query and context
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 2
    input_keys = {var["key"] for var in input_variables}
    assert input_keys == {"query", "context"}

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    output_keys = {var["key"] for var in output_variables}
    assert output_keys == {"text", "chat_history"}

    # AND the workflow deployment tool should have the definition attribute serialized
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    function_attributes = next(
        attribute for attribute in tool_calling_node["attributes"] if attribute["name"] == "functions"
    )
    assert function_attributes["value"]["type"] == "CONSTANT_VALUE"
    assert function_attributes["value"]["value"]["type"] == "JSON"
    workflow_deployment_tool = function_attributes["value"]["value"]["value"][0]

    # AND the workflow deployment tool should have the correct type
    assert workflow_deployment_tool["type"] == "WORKFLOW_DEPLOYMENT"
    assert workflow_deployment_tool["name"] == "weather-workflow-deployment"

    # AND the workflow deployment tool should have a definition attribute (like code tool)
    assert "definition" in workflow_deployment_tool
    definition = workflow_deployment_tool["definition"]

    # AND the definition should match the expected structure with inputs and examples
    context_var = next(var for var in input_variables if var["key"] == "context")
    context_input_variable_id = context_var["id"]

    assert definition == {
        "state": None,
        "cache_config": None,
        "name": "weatherworkflowdeployment",
        "description": "A workflow that gets the weather for a given city and date.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "date": {"type": "string"},
            },
            "required": ["city", "date"],
            "examples": [{"city": "San Francisco", "date": "2025-01-01"}],
        },
        "inputs": {
            "context": {
                "type": "WORKFLOW_INPUT",
                "input_variable_id": context_input_variable_id,
            }
        },
        "forced": None,
        "strict": None,
    }
