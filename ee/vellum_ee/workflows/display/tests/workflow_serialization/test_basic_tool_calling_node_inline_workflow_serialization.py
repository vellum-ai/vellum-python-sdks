from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_inline_workflow.workflow import BasicToolCallingNodeInlineWorkflowWorkflow


def test_serialize_workflow():
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeInlineWorkflowWorkflow)

    serialized_workflow = workflow_display.serialize()

    assert (
        serialized_workflow["workflow_raw_data"]["definition"]["name"] == "BasicToolCallingNodeInlineWorkflowWorkflow"
    )

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]

    assert tool_calling_node["id"] == "21f29cac-da87-495f-bba1-093d423f4e46"
    assert tool_calling_node["label"] == "GetCurrentWeatherNode"
    assert tool_calling_node["type"] == "GENERIC"
    assert tool_calling_node["display_data"] == {
        "position": {"x": 0.0, "y": 0.0},
        "comment": {"value": "\n    A tool calling node that calls the get_current_weather function.\n    "},
    }
    assert tool_calling_node["base"] == {
        "name": "ToolCallingNode",
        "module": ["vellum", "workflows", "nodes", "experimental", "tool_calling_node", "node"],
    }
    assert tool_calling_node["definition"] == {
        "name": "GetCurrentWeatherNode",
        "module": ["tests", "workflows", "basic_tool_calling_node_inline_workflow", "workflow"],
    }
    assert tool_calling_node["trigger"] == {
        "id": "2414743b-b1dd-4552-8abf-9b7481df9762",
        "merge_behavior": "AWAIT_ATTRIBUTES",
    }
    assert tool_calling_node["ports"] == [
        {"id": "3cd6d78c-9dad-42aa-ad38-31f67057c379", "name": "default", "type": "DEFAULT"}
    ]
    assert tool_calling_node["adornments"] is None

    attributes = tool_calling_node["attributes"]
    assert len(attributes) == 5

    ml_model_attr = attributes[0]
    assert ml_model_attr["id"] == "44420e39-966f-4c59-bdf8-6365a61c5d2a"
    assert ml_model_attr["name"] == "ml_model"
    assert ml_model_attr["value"]["type"] == "CONSTANT_VALUE"
    assert ml_model_attr["value"]["value"]["type"] == "STRING"
    assert ml_model_attr["value"]["value"]["value"] == "gpt-4o-mini"

    blocks_attr = attributes[1]
    assert blocks_attr["id"] == "669cfb4b-8c25-460e-8952-b63d91302cbc"
    assert blocks_attr["name"] == "blocks"
    assert blocks_attr["value"]["type"] == "CONSTANT_VALUE"
    assert blocks_attr["value"]["value"]["type"] == "JSON"

    blocks_value = blocks_attr["value"]["value"]["value"]
    assert len(blocks_value) == 2
    assert blocks_value[0]["block_type"] == "CHAT_MESSAGE"
    assert blocks_value[0]["chat_role"] == "SYSTEM"
    assert blocks_value[1]["block_type"] == "CHAT_MESSAGE"
    assert blocks_value[1]["chat_role"] == "USER"

    functions_attr = attributes[2]
    assert functions_attr["id"] == "78324739-ff89-47a5-902b-10da0cb95c6d"
    assert functions_attr["name"] == "functions"
    assert functions_attr["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attr["value"]["value"]["type"] == "JSON"

    functions_value = functions_attr["value"]["value"]["value"]
    assert len(functions_value) == 1
    assert functions_value[0]["type"] == "INLINE_WORKFLOW"

    workflow_data = functions_value[0]["exec_config"]["workflow_raw_data"]
    assert len(workflow_data["nodes"]) == 4
    assert len(workflow_data["edges"]) == 3
    assert workflow_data["definition"]["name"] == "BasicInlineSubworkflowWorkflow"

    prompt_inputs_attr = attributes[3]
    assert prompt_inputs_attr["id"] == "0f6dc102-3460-4963-91fa-7ba85d65ef7a"
    assert prompt_inputs_attr["name"] == "prompt_inputs"
    assert prompt_inputs_attr["value"]["type"] == "DICTIONARY_REFERENCE"

    function_configs_attr = attributes[4]
    assert function_configs_attr["id"] == "a4e3bc9f-7112-4d2f-94fb-7362a85db27a"
    assert function_configs_attr["name"] == "function_configs"
    assert function_configs_attr["value"]["type"] == "CONSTANT_VALUE"
    assert function_configs_attr["value"]["value"]["type"] == "JSON"
    assert function_configs_attr["value"]["value"]["value"] is None

    outputs = tool_calling_node["outputs"]
    assert len(outputs) == 2
    assert outputs[0]["name"] == "text"
    assert outputs[0]["type"] == "STRING"
    assert outputs[1]["name"] == "chat_history"
    assert outputs[1]["type"] == "CHAT_HISTORY"
