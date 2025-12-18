import pytest
from unittest.mock import patch
from uuid import UUID, uuid4
from typing import List

from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.references import LazyReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.state import BaseState
from vellum.workflows.triggers.base import BaseTrigger
from vellum_ee.workflows.display.base import StateValueDisplay, WorkflowInputsDisplay, WorkflowMetaDisplay
from vellum_ee.workflows.display.editor.types import NodeDisplayData
from vellum_ee.workflows.display.nodes.base_node_display import BaseNodeDisplay
from vellum_ee.workflows.display.nodes.types import NodeOutputDisplay
from vellum_ee.workflows.display.nodes.vellum.utils import create_node_input, create_node_input_value_pointer_rules
from vellum_ee.workflows.display.types import WorkflowDisplayContext
from vellum_ee.workflows.display.utils.vellum import (
    ConstantValuePointer,
    InputVariableData,
    InputVariablePointer,
    NodeInputValuePointerRule,
    NodeOutputData,
    NodeOutputPointer,
    TriggerAttributeData,
    TriggerAttributePointer,
    WorkflowStateData,
    WorkflowStatePointer,
    create_node_input_value_pointer_rule,
)
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


class Inputs(BaseInputs):
    example_workflow_input: str


class MyNodeA(BaseNode):
    example_node_input = Inputs.example_workflow_input

    class Outputs(BaseOutputs):
        output: str


class MyNodeADisplay(BaseNodeDisplay[MyNodeA]):
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
                        node_id="f2f8f47a-25de-474c-95d7-df4f9b4cb5ac",
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
                        node_id="f2f8f47a-25de-474c-95d7-df4f9b4cb5ac",
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
                        node_id="f2f8f47a-25de-474c-95d7-df4f9b4cb5ac",
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
            workflow_display_class=BaseWorkflowDisplay,
            workflow_display=WorkflowMetaDisplay(
                entrypoint_node_id=uuid4(),
                entrypoint_node_source_handle_id=uuid4(),
                entrypoint_node_display=NodeDisplayData(),
            ),
            global_workflow_input_displays={
                Inputs.example_workflow_input: WorkflowInputsDisplay(
                    id=UUID("a154c29d-fac0-4cd0-ba88-bc52034f5470"),
                ),
            },
            global_node_output_displays={
                MyNodeA.Outputs.output: NodeOutputDisplay(
                    id=UUID("4b16a629-11a1-4b3f-a965-a57b872d13b8"), name="output"
                ),
            },
            global_node_displays={
                MyNodeA: MyNodeADisplay(),
            },
        ),
        uuid4(),
    )
    assert rules == expected_rules


class MyState(BaseState):
    my_attribute: str


def test_create_node_input_value_pointer_rule__state_value_reference() -> None:
    """
    Tests that StateValueReference is serialized to WorkflowStatePointer using the display override ID.
    """

    # GIVEN a StateValueReference
    state_value_reference: StateValueReference[str] = MyState.my_attribute  # type: ignore[assignment]

    # AND a display context with a state value display override
    override_id = uuid4()
    display_context = WorkflowDisplayContext(
        global_state_value_displays={
            state_value_reference: StateValueDisplay(id=override_id),
        },
    )

    # WHEN we create a node input value pointer rule
    result = create_node_input_value_pointer_rule(state_value_reference, display_context)

    # THEN we should get a WorkflowStatePointer with the overridden display ID
    assert isinstance(result, WorkflowStatePointer)
    assert result.type == "WORKFLOW_STATE"
    assert isinstance(result.data, WorkflowStateData)
    assert result.data.state_variable_id == str(override_id)


class MyTrigger(BaseTrigger):
    my_attribute: str


def test_create_node_input_value_pointer_rule__trigger_attribute_reference() -> None:
    """
    Tests that TriggerAttributeReference is serialized to TriggerAttributePointer.
    """

    # GIVEN a TriggerAttributeReference
    trigger_attribute_reference: TriggerAttributeReference[str] = MyTrigger.my_attribute  # type: ignore[assignment]

    # AND a display context
    display_context = WorkflowDisplayContext()

    # WHEN we create a node input value pointer rule
    result = create_node_input_value_pointer_rule(trigger_attribute_reference, display_context)

    # THEN we should get a TriggerAttributePointer with the correct data
    assert isinstance(result, TriggerAttributePointer)
    assert result.type == "TRIGGER_ATTRIBUTE"
    assert isinstance(result.data, TriggerAttributeData)
    assert result.data.trigger_id == str(MyTrigger.__id__)
    assert result.data.attribute_id == str(trigger_attribute_reference.id)


def test_create_node_input__unexpected_error_returns_node_input_with_empty_rules() -> None:
    """
    Tests that when create_node_input_value_pointer_rules raises an unexpected error,
    create_node_input still returns a NodeInput with empty rules and adds the error to display context.
    """

    # GIVEN a display context
    display_context = WorkflowDisplayContext()

    # AND a node_id and input_name
    node_id = uuid4()
    input_name = "test_input"

    # AND create_node_input_value_pointer_rules will raise an unexpected error
    unexpected_error = RuntimeError("Unexpected error during serialization")
    with patch(
        "vellum_ee.workflows.display.nodes.vellum.utils.create_node_input_value_pointer_rules",
        side_effect=unexpected_error,
    ):
        # WHEN we call create_node_input
        result = create_node_input(
            node_id=node_id,
            input_name=input_name,
            value="test_value",
            display_context=display_context,
        )

    # THEN we should still get a NodeInput with empty rules
    assert result.key == input_name
    assert result.value.rules == []
    assert result.value.combinator == "OR"

    # AND the error should be added to the display context
    errors = list(display_context.errors)
    assert len(errors) == 1
    assert errors[0] is unexpected_error
