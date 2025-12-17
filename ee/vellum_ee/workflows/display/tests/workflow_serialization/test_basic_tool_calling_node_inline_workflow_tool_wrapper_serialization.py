from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_tool_calling_node_inline_workflow_tool_wrapper.workflow import (
    BasicToolCallingNodeInlineWorkflowToolWrapperWorkflow,
)


def test_serialize_workflow__inline_workflow_with_tool_wrapper():
    """
    Tests that an inline workflow with tool wrapper serializes correctly with definition containing inputs and examples.
    """

    # GIVEN a workflow that uses an inline workflow with tool wrapper
    workflow_class = BasicToolCallingNodeInlineWorkflowToolWrapperWorkflow

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=workflow_class)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should include both query and context
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 2
    input_keys = {var["key"] for var in input_variables}
    assert input_keys == {"query", "context"}

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    output_keys = {var["key"] for var in output_variables}
    assert output_keys == {"text", "chat_history"}

    # AND the inline workflow tool should have the definition attribute serialized
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    tool_calling_node = workflow_raw_data["nodes"][1]
    function_attributes = next(
        attribute for attribute in tool_calling_node["attributes"] if attribute["name"] == "functions"
    )
    assert function_attributes["value"]["type"] == "CONSTANT_VALUE"
    assert function_attributes["value"]["value"]["type"] == "JSON"
    inline_workflow_tool = function_attributes["value"]["value"]["value"][0]

    # AND the inline workflow tool should have the correct type
    assert inline_workflow_tool["type"] == "INLINE_WORKFLOW"
    assert inline_workflow_tool["name"] == "BasicInlineSubworkflowWorkflow"

    # AND the inline workflow tool should have a definition attribute (like code tool)
    assert "definition" in inline_workflow_tool
    definition = inline_workflow_tool["definition"]

    # AND the definition should have the function name and parameters
    assert definition["name"] == "basic_inline_subworkflow_workflow"
    assert "parameters" in definition

    # AND the parameters should exclude the context input (provided via tool wrapper)
    parameters = definition["parameters"]
    assert parameters["type"] == "object"
    assert "context" not in parameters["properties"]
    assert "city" in parameters["properties"]
    assert "date" in parameters["properties"]

    # AND the parameters should include examples from the tool wrapper
    assert "examples" in parameters
    assert parameters["examples"] == [{"city": "San Francisco", "date": "2025-01-01"}]

    # AND the definition should have the inputs attribute from the tool wrapper
    assert "inputs" in definition
    inputs = definition["inputs"]
    assert "context" in inputs

    # AND the context input should reference the parent workflow input
    context_input = inputs["context"]
    assert context_input["type"] == "WORKFLOW_INPUT"
    assert "input_variable_id" in context_input
