from typing import Optional, Union

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import InlineSubworkflowNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_node__inline_subworkflow_inputs():
    # GIVEN a main workflow with inputs
    class MainInputs(BaseInputs):
        pass

    # AND an inline subworkflow with inputs
    class NestedInputs(BaseInputs):
        input: str
        input_with_default: str = "default"
        optional_input: Optional[str] = None
        optional_input_with_default: Optional[str] = "optional_default"

    class NestedNode(BaseNode):
        input = NestedInputs.input
        input_with_default = NestedInputs.input_with_default

        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result=f"{self.input}-{self.input_with_default}")

    class NestedWorkflow(BaseWorkflow[NestedInputs, BaseState]):
        graph = NestedNode

        class Outputs(BaseWorkflow.Outputs):
            result = NestedNode.Outputs.result

    class MyInlineSubworkflowNode(InlineSubworkflowNode):
        subworkflow_inputs = {
            "input": "input",
            "input_with_default": "input_with_default",
            "optional_input": "optional_input",
            "optional_input_with_default": "optional_input_with_default",
        }
        subworkflow = NestedWorkflow

    class MainWorkflow(BaseWorkflow[MainInputs, BaseState]):
        graph = MyInlineSubworkflowNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyInlineSubworkflowNode.Outputs.result

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=MainWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the inline subworkflow node should have the correct input variables
    inline_subworkflow_node = next(
        node
        for node in serialized_workflow["workflow_raw_data"]["nodes"]
        if node["id"] == str(MyInlineSubworkflowNode.__id__)
    )

    input_variables = inline_subworkflow_node["data"]["input_variables"]
    assert len(input_variables) == 4

    input_var = next(var for var in input_variables if var["key"] == "input")
    assert input_var["required"] is True
    assert input_var["default"] is None
    assert input_var["type"] == "STRING"

    input_with_default_var = next(var for var in input_variables if var["key"] == "input_with_default")
    assert input_with_default_var["required"] is False
    assert input_with_default_var["default"] == {"type": "STRING", "value": "default"}
    assert input_with_default_var["type"] == "STRING"

    optional_input_var = next(var for var in input_variables if var["key"] == "optional_input")
    assert optional_input_var["required"] is False
    assert optional_input_var["default"] == {"type": "JSON", "value": None}
    assert optional_input_var["type"] == "STRING"

    optional_input_with_default_var = next(
        var for var in input_variables if var["key"] == "optional_input_with_default"
    )
    assert optional_input_with_default_var["required"] is False
    assert optional_input_with_default_var["default"] == {"type": "STRING", "value": "optional_default"}
    assert optional_input_with_default_var["type"] == "STRING"


def test_serialize_workflow_input_required_field_edge_cases():
    """
    Test that the required field is correctly determined for various input type scenarios.
    """

    # GIVEN a workflow with various input type edge cases
    class EdgeCaseInputs(BaseInputs):
        required_str: str
        required_int: int
        optional_str: Optional[str]
        optional_int: Optional[int]
        str_with_default: str = "default_value"
        int_with_default: int = 42
        optional_str_with_default: Optional[str] = "optional_default"
        optional_int_with_default: Optional[int] = 100
        optional_str_none_default: Optional[str] = None
        optional_int_none_default: Optional[int] = None
        union_with_none: Union[str, None] = None

    class EdgeCaseNode(BaseNode):
        required_str = EdgeCaseInputs.required_str
        required_int = EdgeCaseInputs.required_int

        class Outputs(BaseNode.Outputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result="test")

    class EdgeCaseWorkflow(BaseWorkflow[EdgeCaseInputs, BaseState]):
        graph = EdgeCaseNode

        class Outputs(BaseWorkflow.Outputs):
            result = EdgeCaseNode.Outputs.result

    # WHEN the workflow is serialized
    workflow_display = get_workflow_display(workflow_class=EdgeCaseWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the input variables should have correct required field values
    input_variables = serialized_workflow["input_variables"]
    input_vars_by_key = {var["key"]: var for var in input_variables}

    assert input_vars_by_key["required_str"]["required"] is True
    assert input_vars_by_key["required_int"]["required"] is True

    assert input_vars_by_key["optional_str"]["required"] is False
    assert input_vars_by_key["optional_int"]["required"] is False

    assert input_vars_by_key["str_with_default"]["required"] is False
    assert input_vars_by_key["int_with_default"]["required"] is False

    assert input_vars_by_key["optional_str_with_default"]["required"] is False
    assert input_vars_by_key["optional_int_with_default"]["required"] is False

    assert input_vars_by_key["optional_str_none_default"]["required"] is False
    assert input_vars_by_key["optional_int_none_default"]["required"] is False

    assert input_vars_by_key["union_with_none"]["required"] is False
