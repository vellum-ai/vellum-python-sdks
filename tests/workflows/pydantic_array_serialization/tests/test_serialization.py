"""
Test serialization of an array of custom Pydantic models in workflow inputs.

This test verifies that the SDK correctly serializes arrays of Pydantic models
when they are used as code_inputs in a CodeExecutionNode.
"""

from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.pydantic_array_serialization.sandbox import PydanticArrayWorkflow


def test_serialize_pydantic_array_in_code_inputs():
    """
    Tests that an array of custom Pydantic models can be serialized correctly.
    """

    # GIVEN a Workflow with a code execution node that has an array of Pydantic models as input
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=PydanticArrayWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be empty (the Pydantic models are in code_inputs, not workflow inputs)
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 0

    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables[0]["key"] == "result"
    assert output_variables[0]["type"] == "STRING"

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["nodes"]) == 3  # entrypoint, code execution, terminal

    code_execution_node = next((node for node in workflow_raw_data["nodes"] if node["type"] == "CODE_EXECUTION"), None)
    assert code_execution_node is not None

    items_input = next(
        (inp for inp in code_execution_node["inputs"] if inp["key"] == "items"),
        None,
    )
    assert items_input is not None

    assert items_input["value"]["combinator"] == "OR"
    assert len(items_input["value"]["rules"]) == 1

    rule = items_input["value"]["rules"][0]
    assert rule["type"] == "CONSTANT_VALUE"

    constant_data = rule["data"]
    assert constant_data["type"] == "JSON"

    items_value = constant_data["value"]
    assert isinstance(items_value, list)
    assert len(items_value) == 3

    assert not DeepDiff(
        [
            {"name": "item1", "value": 10, "is_active": True},
            {"name": "item2", "value": 20, "is_active": False},
            {"name": "item3", "value": 30, "is_active": True},
        ],
        items_value,
        ignore_order=True,
    )
