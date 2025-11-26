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
        "id": "80ed138a-1127-4c77-ba27-a66a37c92717",
        "name": "functions",
        "value": {
            "type": "ARRAY_REFERENCE",
            "items": [
                {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "85eb3714-5810-4935-9abe-a6112d4c406c",
                            "key": "type",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "MCP_SERVER"}},
                        },
                        {
                            "id": "c9cc0249-c8bd-4b67-9347-c0a210646bcc",
                            "key": "name",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "github"}},
                        },
                        {
                            "id": "b8f99ea6-ae33-4e62-b958-351e7e975bdc",
                            "key": "description",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": ""}},
                        },
                        {
                            "id": "07d62347-5a1b-4b91-90f7-1e313238f2b2",
                            "key": "url",
                            "value": {
                                "type": "CONSTANT_VALUE",
                                "value": {"type": "STRING", "value": "https://api.githubcopilot.com/mcp/"},
                            },
                        },
                        {
                            "id": "b9ef2156-dd84-4a84-91ce-ce590fe2087b",
                            "key": "authorization_type",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "BEARER_TOKEN"}},
                        },
                        {
                            "id": "df799ea3-77bb-40a1-82a1-a5fe343ba68b",
                            "key": "bearer_token_value",
                            "value": {
                                "type": "ENVIRONMENT_VARIABLE",
                                "environment_variable": "GITHUB_PERSONAL_ACCESS_TOKEN",
                            },
                        },
                        {
                            "id": "6e940707-ffe9-4cfb-813e-ddc3a9204ba4",
                            "key": "api_key_header_key",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                        {
                            "id": "2e3db081-7596-4057-b977-be69971d7f87",
                            "key": "api_key_header_value",
                            "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
                        },
                    ],
                    "definition": {"name": "MCPServer", "module": ["vellum", "workflows", "types", "definition"]},
                }
            ],
        },
    }
