from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_tool_wrapper.workflow import BasicToolCallingNodeWrapperWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a tool calling node with tool wrapper
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicToolCallingNodeWrapperWorkflow)

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
    assert input_variables[0]["key"] == "date_input"
    assert input_variables[0]["type"] == "STRING"

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    output_keys = {output["key"] for output in output_variables}
    assert output_keys == {"text", "chat_history"}

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    nodes = workflow_raw_data["nodes"]
    assert len(nodes) == 2

    tool_calling_node = next(node for node in nodes if node.get("type") == "GENERIC")

    functions_attr = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
    functions = functions_attr["value"]["value"]["value"]
    assert len(functions) == 1
    assert functions[0] == {
        "type": "CODE_EXECUTION",
        "name": "get_current_weather",
        "description": "",
        "definition": {
            "state": None,
            "cache_config": None,
            "name": "get_current_weather",
            "description": None,
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The location to get the weather for"},
                    "units": {"type": "string", "description": "The unit of temperature", "default": "fahrenheit"},
                },
                "required": ["location"],
                "examples": [{"location": "San Francisco"}, {"location": "New York", "units": "celsius"}],
            },
            "inputs": {
                "date_input": {
                    "type": "WORKFLOW_INPUT",
                    "input_variable_id": functions[0]["definition"]["inputs"]["date_input"]["input_variable_id"],
                }
            },
            "forced": None,
            "strict": None,
        },
        "src": 'from typing import Annotated\n\n\ndef get_current_weather(\n    date_input: str,\n    location: Annotated[str, "The location to get the weather for"],\n    units: Annotated[str, "The unit of temperature"] = "fahrenheit",\n) -> str:\n    return f"The current weather on {date_input} in {location} is sunny with a temperature of 70 degrees {units}."\n',  # noqa: E501
    }
