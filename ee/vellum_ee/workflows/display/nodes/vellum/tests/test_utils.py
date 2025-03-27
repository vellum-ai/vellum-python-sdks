import pytest
from uuid import UUID, uuid4
from typing import List

from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.references import LazyReference
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input_value_pointer_rules
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import (
    ConstantValuePointer,
    InputVariableData,
    InputVariablePointer,
    NodeInputValuePointerRule,
    NodeOutputData,
    NodeOutputPointer,
)
from vellum_ee.workflows.display.vellum import WorkflowInputsVellumDisplayOverrides, WorkflowMetaVellumDisplay
from vellum_ee.workflows.display.workflows.vellum_workflow_display import VellumWorkflowDisplay


class Inputs(BaseInputs):
    example_workflow_input: str


class MyNodeA(BaseNode):
    example_node_input = Inputs.example_workflow_input

    class Outputs(BaseOutputs):
        output: str


class MyNodeADisplay(BaseNodeVellumDisplay[MyNodeA]):
    pass


class MyNodeB(BaseNode):
    example = MyNodeA.Outputs.output
    fallback_example = MyNodeA.Outputs.output.coalesce(Inputs.example_workflow_input).coalesce("fallback")
    constant_coalesce = Inputs.example_workflow_input.coalesce("default_value")
    lazy_coalesce: BaseDescriptor[str] = LazyReference(
        lambda: MyNodeA.Outputs.output.coalesce(Inputs.example_workflow_input)
    )


@pytest.mark.parametrize(
    ["descriptor", "expected_rules"],
    [
        (
            MyNodeB.example,
            [
                NodeOutputPointer(
                    data=NodeOutputData(
                        node_id="b48fa5e0-d7d3-4fe3-ae48-615415011cc5",
                        output_id="4b16a629-11a1-4b3f-a965-a57b872d13b8",
                    )
                )
            ],
        ),
        (
            MyNodeB.fallback_example,
            [
                NodeOutputPointer(
                    data=NodeOutputData(
                        node_id="b48fa5e0-d7d3-4fe3-ae48-615415011cc5",
                        output_id="4b16a629-11a1-4b3f-a965-a57b872d13b8",
                    ),
                ),
                InputVariablePointer(
                    data=InputVariableData(input_variable_id="a154c29d-fac0-4cd0-ba88-bc52034f5470"),
                ),
                ConstantValuePointer(data=StringVellumValue(value="fallback")),
            ],
        ),
        (
            MyNodeB.constant_coalesce,
            [
                InputVariablePointer(
                    data=InputVariableData(input_variable_id="a154c29d-fac0-4cd0-ba88-bc52034f5470"),
                ),
                ConstantValuePointer(data=StringVellumValue(value="default_value")),
            ],
        ),
        (
            MyNodeB.lazy_coalesce,
            [
                NodeOutputPointer(
                    data=NodeOutputData(
                        node_id="b48fa5e0-d7d3-4fe3-ae48-615415011cc5",
                        output_id="4b16a629-11a1-4b3f-a965-a57b872d13b8",
                    ),
                ),
                InputVariablePointer(
                    data=InputVariableData(input_variable_id="a154c29d-fac0-4cd0-ba88-bc52034f5470"),
                ),
            ],
        ),
    ],
)
def test_create_node_input_value_pointer_rules(
    descriptor: BaseDescriptor, expected_rules: List[NodeInputValuePointerRule]
) -> None:
    rules = create_node_input_value_pointer_rules(
        descriptor,
        WorkflowDisplayContext(
            workflow_display_class=VellumWorkflowDisplay,
            workflow_display=WorkflowMetaVellumDisplay(
                entrypoint_node_id=uuid4(),
                entrypoint_node_source_handle_id=uuid4(),
                entrypoint_node_display=NodeDisplayData(),
            ),
            global_workflow_input_displays={
                Inputs.example_workflow_input: WorkflowInputsVellumDisplayOverrides(
                    id=UUID("a154c29d-fac0-4cd0-ba88-bc52034f5470"),
                ),
            },
            global_node_output_displays={
                MyNodeA.Outputs.output: (
                    MyNodeA,
                    NodeOutputDisplay(id=UUID("4b16a629-11a1-4b3f-a965-a57b872d13b8"), name="output"),
                ),
            },
            global_node_displays={
                MyNodeA: MyNodeADisplay(),
            },
        ),
    )
    assert rules == expected_rules
