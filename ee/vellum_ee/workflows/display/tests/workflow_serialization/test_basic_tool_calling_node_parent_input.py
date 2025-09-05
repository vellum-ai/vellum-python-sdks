from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_parent_input.workflow import BasicToolCallingNodeParentInputWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeParentInputWorkflow)

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
            {"id": "e2e36cfc-cf24-42fd-ba8f-cce39c53d47b", "key": "text", "type": "STRING"},
            {"id": "08ca9519-e421-47e8-a42d-44f49f6aab16", "key": "chat_history", "type": "CHAT_HISTORY"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][2]

    attributes = tool_calling_node["attributes"]
    function_attributes = next(attribute for attribute in attributes if attribute["name"] == "functions")
    assert function_attributes == {
        "id": "cec9f5f2-7bb0-42e4-9c56-f215f07c5569",
        "name": "functions",
        "value": {
            "type": "CONSTANT_VALUE",
            "value": {
                "type": "JSON",
                "value": [
                    {
                        "type": "CODE_EXECUTION",
                        "name": "get_string",
                        "description": "\n    Get a string with the parent input, dummy input, and the populated input.\n    ",  # noqa: E501
                        "definition": {
                            "state": None,
                            "cache_config": None,
                            "name": "get_string",
                            "description": "\n    Get a string with the parent input, dummy input, and the populated input.\n    ",  # noqa: E501
                            "parameters": {
                                "type": "object",
                                "properties": {"populated_input": {"type": "string"}},
                                "required": ["populated_input"],
                            },
                            "inputs": {
                                "parent_input": {
                                    "type": "WORKFLOW_INPUT",
                                    "input_variable_id": "4bf1f0e7-76c6-4204-9f8c-bd9c3b73a8db",
                                },
                                "dummy_input": {
                                    "type": "NODE_OUTPUT",
                                    "node_id": "8e89ae10-a709-45ec-89f8-242f92e4a83f",
                                    "node_output_id": "0cd09f0a-c142-4d5d-acc7-b93cd30ca58d",
                                },
                            },
                            "forced": None,
                            "strict": None,
                        },
                        "src": 'from vellum.workflows.utils.functions import use_tool_inputs\n\nfrom .inputs import ParentInputs\nfrom .nodes.dummy_node import DummyNode\n\n\n@use_tool_inputs(\n    parent_input=ParentInputs.parent_input,\n    dummy_input=DummyNode.Outputs.text,\n)\ndef get_string(parent_input: str, dummy_input: str, populated_input: str) -> str:\n    """\n    Get a string with the parent input, dummy input, and the populated input.\n    """\n    return f"This is the parent input: {parent_input}, this is the dummy input: {dummy_input}, and this is the populated input: {populated_input}"  # noqa: E501\n',  # noqa: E501
                    }
                ],
            },
        },
    }
