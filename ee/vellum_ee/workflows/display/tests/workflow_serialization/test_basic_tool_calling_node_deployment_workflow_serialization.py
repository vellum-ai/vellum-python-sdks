from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_deployment_workflow.workflow import (
    BasicToolCallingNodeDeploymentWorkflowWorkflow,
)


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeDeploymentWorkflowWorkflow)

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
            {"id": "5c740646-7866-447f-b68d-833f3e198c30", "key": "text", "type": "STRING"},
            {"id": "7bd47b06-0481-48a7-a51e-6a998385ee9a", "key": "chat_history", "type": "CHAT_HISTORY"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    assert tool_calling_node == {
        "id": "b6d28aed-a60f-4c29-9d02-6a130358f2be",
        "label": "MyToolCallingNode",
        "type": "GENERIC",
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": {
            "name": "ToolCallingNode",
            "module": ["vellum", "workflows", "nodes", "experimental", "tool_calling_node", "node"],
        },
        "definition": {
            "name": "MyToolCallingNode",
            "module": ["tests", "workflows", "basic_tool_calling_node_deployment_workflow", "workflow"],
        },
        "trigger": {"id": "e7774637-d160-4c4a-8106-4fa15b261f5f", "merge_behavior": "AWAIT_ATTRIBUTES"},
        "ports": [{"id": "9427ace6-cc30-4c4c-ac09-91842e6ca01f", "name": "default", "type": "DEFAULT"}],
        "adornments": None,
        "attributes": [
            {
                "id": "43a479ed-8130-403b-b6d4-e085bab497db",
                "name": "ml_model",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "STRING", "value": "gpt-4"}},
            },
            {
                "id": "f17c7e76-5696-485f-92a7-45dfc94b10fb",
                "name": "blocks",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": [
                            {
                                "block_type": "CHAT_MESSAGE",
                                "state": None,
                                "cache_config": None,
                                "chat_role": "SYSTEM",
                                "chat_source": None,
                                "chat_message_unterminated": None,
                                "blocks": [
                                    {
                                        "block_type": "RICH_TEXT",
                                        "state": None,
                                        "cache_config": None,
                                        "blocks": [
                                            {
                                                "block_type": "PLAIN_TEXT",
                                                "state": None,
                                                "cache_config": None,
                                                "text": "You are a helpful assistant. Use the available tools to help the user.",  # noqa: E501
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "block_type": "CHAT_MESSAGE",
                                "state": None,
                                "cache_config": None,
                                "chat_role": "USER",
                                "chat_source": None,
                                "chat_message_unterminated": None,
                                "blocks": [
                                    {
                                        "block_type": "RICH_TEXT",
                                        "state": None,
                                        "cache_config": None,
                                        "blocks": [
                                            {
                                                "block_type": "VARIABLE",
                                                "state": None,
                                                "cache_config": None,
                                                "input_variable": "query",
                                            }
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                },
            },
            {
                "id": "73a94e3c-1935-4308-a68a-ecd5441804b7",
                "name": "functions",
                "value": {
                    "type": "CONSTANT_VALUE",
                    "value": {
                        "type": "JSON",
                        "value": [
                            {"type": "DEPLOYMENT_WORKFLOW", "deployment": "deployment_1", "release_tag": "LATEST"}
                        ],
                    },
                },
            },
            {
                "id": "f8ef2b4f-4c43-4d24-84b1-63081e5fc490",
                "name": "prompt_inputs",
                "value": {
                    "type": "DICTIONARY_REFERENCE",
                    "entries": [
                        {
                            "id": "50c33b12-7263-4803-9363-946b7dc5e92a",
                            "key": "query",
                            "value": {
                                "type": "WORKFLOW_INPUT",
                                "input_variable_id": "8eb6877a-7a92-439b-8355-124c5880a94d",
                            },
                        }
                    ],
                },
            },
            {
                "id": "bff4a5b8-d8cd-4f34-bf59-eac7a5131c00",
                "name": "function_configs",
                "value": {"type": "CONSTANT_VALUE", "value": {"type": "JSON", "value": None}},
            },
        ],
        "outputs": [
            {"id": "de0286f1-d33f-4953-9808-3aa8330af2d6", "name": "text", "type": "STRING", "value": None},
            {
                "id": "77bc809c-4d17-4e61-ac7d-93da4d17a40f",
                "name": "chat_history",
                "type": "CHAT_HISTORY",
                "value": None,
            },
        ],
    }
