from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_with_composio_tool.workflow import (
    BasicToolCallingNodeWithComposioToolWorkflow,
)


def test_serialize_workflow():
    # GIVEN a Workflow that uses a tool calling node with a composio tool
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeWithComposioToolWorkflow)

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

    # Find the text and chat_history outputs
    text_output = next(var for var in output_variables if var["key"] == "text")
    chat_history_output = next(var for var in output_variables if var["key"] == "chat_history")

    assert text_output["type"] == "STRING"
    assert chat_history_output["type"] == "CHAT_HISTORY"

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]

    # AND the tool calling node should have the composio tool properly serialized
    functions_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
    assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attribute["value"]["value"]["type"] == "JSON"

    functions_list = functions_attribute["value"]["value"]["value"]
    assert len(functions_list) == 1

    composio_function = functions_list[0]
    assert composio_function == {
        "type": "COMPOSIO",
        "toolkit": "GITHUB",
        "action": "GITHUB_CREATE_AN_ISSUE",
        "description": "Create a new issue in a GitHub repository",
        "user_id": None,
        "name": "github_create_an_issue",
    }

    # AND the rest of the node structure should be correct
    assert tool_calling_node["type"] == "GENERIC"
    assert tool_calling_node["base"]["name"] == "ToolCallingNode"
    assert tool_calling_node["definition"]["name"] == "ComposioToolCallingNode"

    # AND the blocks should be properly serialized
    blocks_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "blocks")
    assert blocks_attribute["value"]["type"] == "CONSTANT_VALUE"
    blocks_list = blocks_attribute["value"]["value"]["value"]
    assert len(blocks_list) == 2
    assert blocks_list[0]["chat_role"] == "SYSTEM"
    assert blocks_list[1]["chat_role"] == "USER"

    # AND the prompt inputs should be properly serialized
    prompt_inputs_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "prompt_inputs")
    assert prompt_inputs_attribute["value"]["type"] == "DICTIONARY_REFERENCE"
    entries = prompt_inputs_attribute["value"]["entries"]
    assert len(entries) == 1
    assert entries[0]["key"] == "question"
    assert entries[0]["value"]["type"] == "WORKFLOW_INPUT"

    # AND the outputs should be correct
    outputs = tool_calling_node["outputs"]
    assert len(outputs) == 2
    assert outputs[0]["name"] == "text"
    assert outputs[0]["type"] == "STRING"
    assert outputs[1]["name"] == "chat_history"
    assert outputs[1]["type"] == "CHAT_HISTORY"
