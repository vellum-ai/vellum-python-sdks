from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_mcp_tool.workflow import BasicToolCallingNodeMCPWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeMCPWorkflow)

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

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {"id": "3934525a-4807-4dd3-a44f-8569033fece1", "key": "text", "type": "STRING"},
            {"id": "a6ba35f0-306b-45a4-ad79-c1e9b9a5515c", "key": "chat_history", "type": "CHAT_HISTORY"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    function_attributes = next(
        (attribute for attribute in tool_calling_node["attributes"] if attribute["name"] == "functions"),
    )
    assert function_attributes == {
        "id": "20adf593-c4f0-4c67-8e36-37eb66f28f66",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "MCP_SERVER",
                        "name": "github",
                        "description": "",
                        "url": "https://api.githubcopilot.com/mcp/",
                        "authorization_type": "BEARER_TOKEN",
                        "bearer_token_value": "GITHUB_PERSONAL_ACCESS_TOKEN",
                        "api_key_header_key": None,
                        "api_key_header_value": None,
                    }
                ],
            },
        },
    }
