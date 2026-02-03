from unittest import mock
from unittest.mock import ANY, patch
from typing import Any, Dict, List, cast

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.context import WorkflowContext
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class SimpleClass:
    """A simple class with str and int kwargs in __init__."""

    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count


def test_serialize_workflow__code_tool_with_simple_class_type__serializes_successfully():
    """
    Tests that a code tool with a simple class parameter serializes successfully.
    """

    # GIVEN a function with a simple class parameter
    def my_tool_with_class_param(data: SimpleClass) -> str:
        return data.name

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_class_param]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized = workflow_display.serialize()

    # THEN the serialization should succeed with no errors
    assert serialized is not None
    assert "workflow_raw_data" in serialized

    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 0

    # AND the functions attribute should have the correct shape with SimpleClass properties
    workflow_raw_data = cast(Dict[str, Any], serialized["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])
    tool_calling_node = next(
        node for node in nodes if (node.get("definition") or {}).get("name") == "MyToolCallingNode"
    )
    functions_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
    assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
    assert functions_attribute["value"]["value"]["type"] == "JSON"

    functions_value = functions_attribute["value"]["value"]["value"]

    # AND the functions attribute should have the correct shape with SimpleClass properties
    simple_class_ref = (
        "vellum_ee.workflows.display.tests.workflow_serialization.test_code_tool_function_type_error.SimpleClass"
    )
    expected = [
        {
            "type": "CODE_EXECUTION",
            "name": "my_tool_with_class_param",
            "description": "",
            "definition": {
                "state": None,
                "cache_config": None,
                "name": "my_tool_with_class_param",
                "description": None,
                "parameters": {
                    "type": "object",
                    "properties": {"data": {"$ref": f"#/$defs/{simple_class_ref}"}},
                    "required": ["data"],
                    "$defs": {
                        simple_class_ref: {
                            "type": "object",
                            "properties": {"name": {"type": "string"}, "count": {"type": "integer"}},
                            "required": ["name", "count"],
                        }
                    },
                },
                "inputs": None,
                "forced": None,
                "strict": None,
            },
            "src": ANY,
        }
    ]
    assert expected == functions_value


def test_serialize_workflow__code_tool_with_workflow_context_type__serializes_successfully():
    """
    Tests that a code tool with a WorkflowContext parameter serializes successfully.
    The WorkflowContext parameter should be excluded from the function schema.
    """

    # GIVEN a function with a WorkflowContext parameter
    def my_tool_with_context(ctx: WorkflowContext, query: str) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_context]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized = workflow_display.serialize()

    # THEN the serialization should succeed with no errors
    assert serialized is not None
    assert "workflow_raw_data" in serialized

    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 0

    # AND the functions attribute should contain the function definition with WorkflowContext excluded
    workflow_raw_data = cast(Dict[str, Any], serialized["workflow_raw_data"])
    nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])
    tool_calling_node = next(
        node for node in nodes if (node.get("definition") or {}).get("name") == "MyToolCallingNode"
    )
    functions_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
    functions_value = functions_attribute["value"]["value"]["value"]

    # AND the full functions_value should match the expected structure
    # Note: 'src' field is dynamic (contains the source file content), so we use mock.ANY
    assert functions_value == [
        {
            "type": "CODE_EXECUTION",
            "name": "my_tool_with_context",
            "description": "",
            "definition": {
                "state": None,
                "cache_config": None,
                "name": "my_tool_with_context",
                "description": None,
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
                "inputs": None,
                "forced": None,
                "strict": None,
            },
            "src": mock.ANY,
        }
    ]

    # AND specifically verify the WorkflowContext parameter 'ctx' is NOT in the parameters
    definition = functions_value[0]["definition"]
    assert "ctx" not in definition["parameters"]["properties"]


def test_serialize_workflow__compile_function_definition_raises_value_error__error_in_display_context():
    """
    Tests that a ValueError from compile_function_definition is captured in display_context.errors.
    """

    # GIVEN a simple function
    def my_simple_tool(query: str) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_simple_tool]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # AND compile_function_definition is mocked to raise a ValueError
    with patch("vellum_ee.workflows.display.utils.expressions.compile_function_definition") as mock_compile:
        mock_compile.side_effect = ValueError("Failed to compile type: <class 'SomeUnknownType'>")

        # WHEN we serialize the workflow with dry_run=True
        workflow_display = get_workflow_display(workflow_class=TestWorkflow, dry_run=True)
        serialized = workflow_display.serialize()

        # THEN the serialization should succeed
        assert serialized is not None
        assert "workflow_raw_data" in serialized

        # AND the error should be captured in display_context.errors
        errors = list(workflow_display.display_context.errors)
        assert len(errors) > 0

        # AND the error message should contain the original ValueError message
        error_messages = [str(e) for e in errors]
        assert any("my_simple_tool" in msg for msg in error_messages)
        assert any("Failed to compile type" in msg for msg in error_messages)

        # AND the tool calling node's functions attribute should have an empty list
        workflow_raw_data = cast(Dict[str, Any], serialized["workflow_raw_data"])
        nodes = cast(List[Dict[str, Any]], workflow_raw_data["nodes"])
        tool_calling_node = next(
            node for node in nodes if (node.get("definition") or {}).get("name") == "MyToolCallingNode"
        )
        functions_attribute = next(attr for attr in tool_calling_node["attributes"] if attr["name"] == "functions")
        assert functions_attribute["value"]["type"] == "CONSTANT_VALUE"
        assert functions_attribute["value"]["value"]["type"] == "JSON"
        assert functions_attribute["value"]["value"]["value"] == []
