import logging
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from vellum.client.core.api_error import ApiError
from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.array_vellum_value import ArrayVellumValue
from vellum.client.types.vellum_value import VellumValue
from vellum.client.types.vellum_variable_type import VellumVariableType
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value
from vellum.workflows.nodes.utils import get_unadorned_node
from vellum.workflows.references import OutputReference, WorkflowInputReference
from vellum.workflows.references.environment_variable import EnvironmentVariableReference
from vellum.workflows.references.execution_count import ExecutionCountReference
from vellum.workflows.references.lazy import LazyReference
from vellum.workflows.references.node import NodeReference
from vellum.workflows.references.state_value import StateValueReference
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.utils.functions import compile_annotation
from vellum.workflows.utils.vellum_variables import primitive_type_to_vellum_variable_type
from vellum_ee.workflows.display.utils.exceptions import (
    InvalidInputReferenceError,
    InvalidOutputReferenceError,
    UnsupportedSerializationException,
)
from vellum_ee.workflows.display.utils.expressions import get_child_descriptor

if TYPE_CHECKING:
    from vellum_ee.workflows.display.types import WorkflowDisplayContext

logger = logging.getLogger(__name__)


class ConstantValuePointer(UniversalBaseModel):
    type: Literal["CONSTANT_VALUE"] = "CONSTANT_VALUE"
    data: VellumValue


ArrayVellumValue.model_rebuild()


class NodeOutputData(UniversalBaseModel):
    node_id: str
    output_id: str


class NodeOutputPointer(UniversalBaseModel):
    type: Literal["NODE_OUTPUT"] = "NODE_OUTPUT"
    data: NodeOutputData


class InputVariableData(UniversalBaseModel):
    input_variable_id: str


class InputVariablePointer(UniversalBaseModel):
    type: Literal["INPUT_VARIABLE"] = "INPUT_VARIABLE"
    data: InputVariableData


class WorkspaceSecretData(UniversalBaseModel):
    type: VellumVariableType
    workspace_secret_id: Optional[str] = None


class WorkspaceSecretPointer(UniversalBaseModel):
    type: Literal["WORKSPACE_SECRET"] = "WORKSPACE_SECRET"
    data: WorkspaceSecretData


class ExecutionCounterData(UniversalBaseModel):
    node_id: str


class ExecutionCounterPointer(UniversalBaseModel):
    type: Literal["EXECUTION_COUNTER"] = "EXECUTION_COUNTER"
    data: ExecutionCounterData


class EnvironmentVariableData(UniversalBaseModel):
    environment_variable: str


class EnvironmentVariablePointer(UniversalBaseModel):
    type: Literal["ENVIRONMENT_VARIABLE"] = "ENVIRONMENT_VARIABLE"
    data: EnvironmentVariableData


class WorkflowStateData(UniversalBaseModel):
    state_variable_id: str


class WorkflowStatePointer(UniversalBaseModel):
    type: Literal["WORKFLOW_STATE"] = "WORKFLOW_STATE"
    data: WorkflowStateData


class TriggerAttributeData(UniversalBaseModel):
    trigger_id: str
    attribute_id: str


class TriggerAttributePointer(UniversalBaseModel):
    type: Literal["TRIGGER_ATTRIBUTE"] = "TRIGGER_ATTRIBUTE"
    data: TriggerAttributeData


NodeInputValuePointerRule = Union[
    NodeOutputPointer,
    InputVariablePointer,
    ConstantValuePointer,
    WorkspaceSecretPointer,
    ExecutionCounterPointer,
    EnvironmentVariablePointer,
    WorkflowStatePointer,
    TriggerAttributePointer,
]


def infer_vellum_variable_type(value: Any) -> VellumVariableType:
    inferred_type: VellumVariableType

    if isinstance(value, BaseDescriptor):
        descriptor: BaseDescriptor = value
        if isinstance(descriptor, NodeReference):
            if not isinstance(descriptor.instance, BaseDescriptor):
                raise ValueError(
                    f"Expected NodeReference {descriptor.name} to have an instance pointing to a descriptor"
                )
            descriptor = descriptor.instance

        inferred_type = primitive_type_to_vellum_variable_type(descriptor)
    else:
        vellum_variable_value = primitive_to_vellum_value(value)
        inferred_type = vellum_variable_value.type

    return inferred_type


def compile_descriptor_annotation(descriptor: BaseDescriptor) -> dict:
    """Compile a BaseDescriptor's type annotation to a JSON schema."""
    if not descriptor.types:
        return {}
    return compile_annotation(descriptor.normalized_type, {})


def create_node_input_value_pointer_rule(
    value: Any, display_context: "WorkflowDisplayContext"
) -> NodeInputValuePointerRule:
    if isinstance(value, OutputReference):
        if value not in display_context.global_node_output_displays:
            if issubclass(value.outputs_class, BaseNode.Outputs):
                raise ValueError(
                    f"Reference to node '{value.outputs_class.__parent_class__.__name__}' not found in graph."
                )

            raise ValueError(f"Reference to outputs '{value.outputs_class.__qualname__}' is invalid.")

        output_display = display_context.global_node_output_displays[value]

        upstream_node_class = value.outputs_class.__parent_class__
        if not issubclass(upstream_node_class, BaseNode):
            raise ValueError(f"Output references must be to a node, not {upstream_node_class}")
        unadorned_upstream_node_class = get_unadorned_node(upstream_node_class)
        upstream_node_display = display_context.global_node_displays[unadorned_upstream_node_class]

        return NodeOutputPointer(
            data=NodeOutputData(node_id=str(upstream_node_display.node_id), output_id=str(output_display.id)),
        )
    if isinstance(value, LazyReference):
        try:
            child_descriptor = get_child_descriptor(value, display_context)
        except InvalidOutputReferenceError as e:
            logger.warning("Failed to parse lazy reference '%s', skipping serialization", value.name)
            display_context.add_validation_error(e)
            raise UnsupportedSerializationException(f"Failed to parse lazy reference: {value.name}")
        return create_node_input_value_pointer_rule(child_descriptor, display_context)
    if isinstance(value, WorkflowInputReference):
        if value not in display_context.global_workflow_input_displays:
            raise InvalidInputReferenceError(
                message=f"Inputs class '{value.inputs_class.__qualname__}' has no attribute '{value.name}'",
                inputs_class_name=value.inputs_class.__qualname__,
                attribute_name=value.name,
            )
        workflow_input_display = display_context.global_workflow_input_displays[value]
        return InputVariablePointer(data=InputVariableData(input_variable_id=str(workflow_input_display.id)))
    if isinstance(value, VellumSecretReference):
        try:
            workspace_secret = display_context.client.workspace_secrets.retrieve(
                id=value.name,
            )
            workspace_secret_id: Optional[str] = str(workspace_secret.id)
        except ApiError:
            workspace_secret_id = None

        return WorkspaceSecretPointer(
            data=WorkspaceSecretData(
                type="STRING",
                workspace_secret_id=workspace_secret_id,
            ),
        )
    if isinstance(value, ExecutionCountReference):
        node_class_display = display_context.node_displays[value.node_class]
        return ExecutionCounterPointer(
            data=ExecutionCounterData(node_id=str(node_class_display.node_id)),
        )
    if isinstance(value, EnvironmentVariableReference):
        return EnvironmentVariablePointer(
            data=EnvironmentVariableData(
                environment_variable=value.name,
            ),
        )
    if isinstance(value, StateValueReference):
        state_value_display = display_context.global_state_value_displays[value]
        return WorkflowStatePointer(
            data=WorkflowStateData(
                state_variable_id=str(state_value_display.id),
            ),
        )
    if isinstance(value, TriggerAttributeReference):
        return TriggerAttributePointer(
            data=TriggerAttributeData(
                trigger_id=str(value.trigger_class.__id__),
                attribute_id=str(value.id),
            ),
        )

    if not isinstance(value, BaseDescriptor):
        vellum_value = primitive_to_vellum_value(value)
        return ConstantValuePointer(type="CONSTANT_VALUE", data=vellum_value)

    raise UnsupportedSerializationException(f"Unsupported descriptor type: {value.__class__.__name__}")
