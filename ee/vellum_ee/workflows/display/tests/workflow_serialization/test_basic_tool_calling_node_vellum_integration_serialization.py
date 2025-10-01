from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_with_vellum_integration_tool.workflow import (
    BasicToolCallingNodeWithVellumIntegrationToolWorkflow,
)


def test_serialize_workflow():
    # GIVEN a Workflow that uses a tool calling node with a vellum integration tool
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeWithVellumIntegrationToolWorkflow)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert input_variables[0]["key"] == "query"
    assert input_variables[0]["type"] == "STRING"

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2

    # Find the text and chat_history outputs
    text_output = next(var for var in output_variables if var["key"] == "text")
    chat_history_output = next(var for var in output_variables if var["key"] == "chat_history")

    assert text_output["type"] == "STRING"
    assert chat_history_output["type"] == "CHAT_HISTORY"

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]

    # Tool calling nodes serialize as GENERIC nodes
    assert tool_calling_node["type"] == "GENERIC"
    assert tool_calling_node["label"] == "Vellum Integration Tool Calling Node"

    # Verify the node base class
    assert tool_calling_node["base"]["name"] == "ToolCallingNode"

    # Verify the node has the expected attributes with function definitions
    assert "attributes" in tool_calling_node
    attributes = tool_calling_node["attributes"]

    # Find the functions attribute
    functions_attr = next(attr for attr in attributes if attr["name"] == "functions")
    assert functions_attr["value"]["type"] == "CONSTANT_VALUE"

    # Verify the function definition details
    functions_value = functions_attr["value"]["value"]["value"]
    assert len(functions_value) == 1

    function = functions_value[0]
    assert function["type"] == "VELLUM_INTEGRATION"
    assert function["provider"] == "COMPOSIO"  # VellumIntegrationProviderType.COMPOSIO
    assert function["integration_name"] == "GITHUB"
    assert function["name"] == "create_issue"
    assert function["description"] == "Create a new issue in a GitHub repository"
